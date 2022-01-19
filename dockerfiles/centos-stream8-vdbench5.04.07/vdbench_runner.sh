#!/bin/bash

#for local testing with podman I run this
#podman run -v /workload:/workload -e MIX_PRECENTAGE=,,,,,, -e RUN_FILLUP=yes -e WARMUP=0 -e IO_RATE=200,max -e COMPRESSION_RATIO=2 -e FILES_IO=random,random -e FILES_SELECTION=random -e SIZE_PER_FILE=10 -e DIRECTORIES=300 -e FILES_PER_DIRECTORY=3 -e BLOCK_SIZES=16,64_cache  -e IO_OPERATION=read,write -e IO_THREADS=1,1  -e DURATION=20 -e PAUSE=0 -v /root/vdpod:/vdpod/config -it quay.io/bbenshab/centos-vdbench-pod:latest

#intenal
declare error="[warning]"
declare workload_path="/workload"
declare tmp_test_file=`mktemp`
declare dbs_patterns=("oltp1" "oltp2" "oltphw" "odss2" "odss128")
declare fillup_max_data
declare -A fwd_list
declare -A wd_list

#workload user params
declare block_size
declare io_operation
declare files_io
declare files_selection
declare io_threads
declare io_rate
declare mix_precentage

#workload global params
declare compression_ratio
declare tests_pause
declare tests_duration
declare run_fillup
declare warmup

#dataset params
declare directories
declare files_per_directory
declare size_per_file


get_tests_parms_from_env(){
    IFS=, read -a block_size <<<$(echo $BLOCK_SIZES)
    IFS=, read -a io_operation <<<$(echo $IO_OPERATION)
    IFS=, read -a io_threads <<<$(echo $IO_THREADS)
    IFS=, read -a files_io <<<$(echo $FILES_IO)
    IFS=, read -a io_rate <<<$(echo $IO_RATE)
    IFS=, read -a mix_precentage <<<$(echo $MIX_PRECENTAGE)
    tests_duration=$(echo $DURATION)
    tests_pause=$(echo $PAUSE)
    directories=$(echo $DIRECTORIES)
    files_per_directory=$(echo $FILES_PER_DIRECTORY)
    size_per_file=$(echo $SIZE_PER_FILE)
    files_selection=$(echo $FILES_SELECTION)
    compression_ratio=$(echo $COMPRESSION_RATIO)
    warmup=$(echo $WARMUP)
    fillup_max_data=$((${directories}*${files_per_directory}*${size_per_file})) 
    run_fillup=$(echo $RUN_FILLUP)
}

generate_workload_config(){
    local r

    #general settings
    echo "create_anchors=yes"
    echo "data_errors=1000"
    echo "compratio=${compression_ratio}"
    #host general definition
    echo "hd=default,user=root,shell=ssh,vdbench=/vdbench,jvms=1"

    #default file stracture
    echo "fsd=default,depth=0,width=${directories},files=${files_per_directory},size=${size_per_file}mb"

    #create drive definition
    echo "fsd=fsd0,anchor=${workload_path}"

    #generate fillup definition
    if [[ ${run_fillup} = "yes" ]];  then
	echo "fwd=fillup,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=sequential,xfersize=1024k,threads=1"
    fi

    #generate workload definition
    check_if_cache_or_mixed_cache(){
	local r=$1
	local real_size
	local write_precent
        real_size=$(echo ${block_size[$r]} | sed 's/[^0-9]*//g')
        if [ ${io_operation[$r]} = "read" ] && [ -z "${mix_precentage[$r]}" ]; then
	    echo "fwd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${real_size}k,rdpct=100"
	    wd_list[$r]="rd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}"
	elif [ ${io_operation[$r]} = "read" ] && [ -n "${mix_precentage[$r]}" ]; then
	    echo "fwd=${real_size}kb_cache_${}pct_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${real_size}k,rdpct=${mix_precentage[$r]}"
	    wd_list[$r]="rd=${real_size}kb_cache_${mix_precentage[$r]}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${real_size}kb_cache_${mix_precentage[$r]}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}"
	fi
        if [ ${io_operation[$r]} = "write" ] && [ -z ${mix_precentage[$r]} ]; then
            echo "fwd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${real_size}k,rdpct=0"
	    wd_list[$r]="rd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${real_size}kb_cache_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}"
        elif [ ${io_operation[$r]} = "write" ] && [ -n ${mix_precentage[$r]} ];  then
            write_precent=$((100-${mix_precentage[$r]}))
            echo "fwd=${real_size}kb_cache_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${real_size}k,rdpct=${write_precent}"
	    wd_list[$r]="rd=${real_size}kb_cache_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${real_size}kb_cache_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}"
	fi
    }

    check_if_mixed_read_write(){
	local r=$1
	local write_precent
        if [ "${io_operation[$r]}" = "read" ] && [ -z "${mix_precentage[$r]}" ]; then
	    echo "fwd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,openflags=directio,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${block_size[$r]}k,rdpct=100"
            wd_list[$r]=$(echo "rd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}")
        elif [ "${io_operation[$r]}" = "read" ] && [ -n "${mix_precentage[$r]}" ]; then
	    echo "fwd=${block_size[$r]}kb_${mix_precentage[$r]}pct_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,openflags=directio,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${block_size[$r]}k,rdpct=${mix_precentage[$r]}"
	    wd_list[$r]=$(echo "rd=${block_size[$r]}kb_${mix_precentage[$r]}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwd=${block_size[$r]}kb_${mix_precentage[$r]}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}")
	fi
        if [ "${io_operation[$r]}" = "write" ] && [ -z "${mix_precentage[$r]}" ]; then
	    echo "fwd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,openflags=directio,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${block_size[$r]}k,rdpct=0"
	    wd_list[$r]=$(echo "rd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,fwd=${block_size[$r]}kb_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}")
        elif [ "${io_operation[$r]}" = "write" ] && [ -n "${mix_precentage[$r]}" ];  then
            write_precent=$((100-${mix_precentage[$r]}))
	    echo "fwd=${block_size[$r]}kb_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fsd=fsd0,openflags=directio,operation=${io_operation[$r]},fileio=${files_io[$r]},fileselect=${files_selection},xfersize=${block_size[$r]}k,rdpct=${mix_precentage[$r]}"
	    wd_list[$r]=$(echo "rd=fwd=${block_size[$r]}kb_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwd=fwd=${block_size[$r]}kb_${write_precent}pct_${io_operation[$r]}_${io_threads[$r]}threads,fwdrate=${io_rate[$r]},format=restart,elapsed=${tests_duration},interval=5,warmup=${warmup},threads=${io_threads[$r]},pause=${tests_pause}")
	fi
    }

    for ((r=0; r < ${#block_size[@]} ; r++)); do
	if [[ ${block_size[$r]} = "oltp1" ]];  then
	    echo "fwd=oltp1_1,fsd=fsd0,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=10,threads=16"
	    echo "fwd=oltp1_2,fsd=fsd0,openflags=directio,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=35,threads=16"
	    echo "fwd=oltp1_3,fsd=fsd0,openflags=directio,operation=write,fileio=random,fileselect=random,xfersize=4k,rdpct=0,skew=35,threads=16"
	    echo "fwd=oltp1_4,fsd=fsd0,openflags=directio,operation=read,fileio=sequential,fileselect=random,xfersize=4k,skew=5,threads=16"
	    echo "fwd=oltp1_5,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=random,xfersize=4k,skew=15,threads=16"
	elif [[ ${block_size[$r]} = "oltp2" ]];  then
	    echo "fwd=oltp2_1,fsd=fsd0,operation=read,fileio=random,fileselect=random,xfersize=8k,rdpct=100,skew=20,threads=16"
	    echo "fwd=oltp2_2,fsd=fsd0,openflags=directio,operation=read,fileio=random,fileselect=random,xfersize=8k,rdpct=100,skew=45,threads=16"
	    echo "fwd=oltp2_3,fsd=fsd0,openflags=directio,operation=write,fileio=random,fileselect=random,xfersize=8k,rdpct=0,skew=15,threads=16"
	    echo "fwd=oltp2_4,fsd=fsd0,openflags=directio,operation=read,fileio=sequential,fileselect=sequential,xfersize=64k,skew=10,threads=16"
	    echo "fwd=oltp2_5,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=sequential,xfersize=64k,skew=10,threads=16"
	elif [[ ${block_size[$r]} = "oltphw" ]];  then
	    echo "fwd=oltphw_1,fsd=fsd0,operation=read,fileio=random,fileselect=random,xfersize=8k,rdpct=100,skew=10,threads=16"
	    echo "fwd=oltphw_2,fsd=fsd0,openflags=directio,operation=read,fileio=random,fileselect=random,xfersize=8k,rdpct=100,skew=35,threads=16"
	    echo "fwd=oltphw_3,fsd=fsd0,openflags=directio,operation=write,fileio=random,fileselect=random,xfersize=8k,rdpct=0,skew=35,threads=16"
	    echo "fwd=oltphw_4,fsd=fsd0,openflags=directio,operation=read,fileio=sequential,fileselect=sequential,xfersize=64k,skew=5,threads=16"
	    echo "fwd=oltphw_5,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=sequential,xfersize=64k,skew=15,threads=16"
        elif [[ ${block_size[$r]} = "odss2" ]];  then
	    echo "fwd=odss2_1_vm0,fsd=fsd0,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=0,threads=16"
	    echo "fwd=odss2_2_vm0,fsd=fsd0,openflags=directio,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=15,threads=16"
	    echo "fwd=odss2_3_vm0,fsd=fsd0,openflags=directio,operation=write,fileio=random,fileselect=random,xfersize=4k,rdpct=0,skew=5,threads=16"
	    echo "fwd=odss2_4_vm0,fsd=fsd0,openflags=directio,operation=read,fileio=sequential,fileselect=sequential,xfersize=64k,skew=70,threads=16"
	    echo "fwd=odss2_5_vm0,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=sequential,xfersize=64k,skew=10,threads=16"
	elif [[ ${block_size[$r]} = "odss128" ]];  then
	    echo "fwd=odss128_1,fsd=fsd0,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=18,threads=16"
	    echo "fwd=odss128_2,fsd=fsd0,openflags=directio,operation=read,fileio=random,fileselect=random,xfersize=4k,rdpct=100,skew=18,threads=16"
	    echo "fwd=odss128_3,fsd=fsd0,openflags=directio,operation=write,fileio=random,fileselect=random,xfersize=4k,rdpct=0,skew=4,threads=16"
	    echo "fwd=odss128_4,fsd=fsd0,openflags=directio,operation=read,fileio=sequential,fileselect=sequential,xfersize=64k,skew=48,threads=16"
	    echo "fwd=odss128_5,fsd=fsd0,openflags=directio,operation=write,fileio=sequential,fileselect=sequential,xfersize=64k,skew=12,threads=16"
	elif [[ ${block_size[$r],,} = *"cache"* ]];  then
	    check_if_cache_or_mixed_cache $r
	else
	    check_if_mixed_read_write $r
	fi
    done

    #generate fillup run definition
    if [[ ${run_fillup} = "yes" ]];  then
	echo "rd=fillup,fwd=fillup,fwdrate=max,format=restart,elapsed=10000000,interval=5,warmup=0,threads=1,pause=${tests_pause},maxdata=${fillup_max_data}mb"
    fi

    #generate db's work definition
    for ((r=0; r < ${#block_size[@]} ; r++)); do
	if [[ ${block_size[$r]} = "oltp1" ]];  then
	    echo "rd=oltp1,fwd=oltp1_*,fwdrate=${io_rate[$r]},format=(restart,yes),elapsed=${tests_duration},interval=5,threads=${io_threads[$r]},pause=${tests_pause},warmup=${warmup}"
	elif [[ ${block_size[$r]} = "oltp2" ]];  then
            echo "rd=oltp2,fwd=oltp2_*,fwdrate=${io_rate[$r]},format=(restart,yes),elapsed=${tests_duration},interval=5,threads=${io_threads[$r]},pause=${tests_pause},warmup=${warmup}"
        elif [[ ${block_size[$r]} = "oltphw" ]];  then
            echo "rd=oltphw,fwd=oltphw_*,fwdrate=${io_rate[$r]},format=(restart,yes),elapsed=${tests_duration},interval=5,threads=${io_threads[$r]},pause=${tests_pause},warmup=${warmup}"
        elif [[ ${block_size[$r]} = "odss2" ]];  then
            echo "rd=odss2,fwd=odss2_*,fwdrate=${io_rate[$r]},format=(restart,yes),elapsed=${tests_duration},interval=5,threads=${io_threads[$r]},pause=${tests_pause},warmup=${warmup}"
            echo "rd=odss128,fwd=odss128_*,fwdrate=${io_rate[$r]},format=(restart,yes),elapsed=${tests_duration},interval=5,threads=${io_threads[$r]},pause=${tests_pause},warmup=${warmup}"
	fi
    done
    printf '%s\n' "${wd_list[@]}"
}

test_user_settings(){
    should_exit="0"
    check_matching_values(){
	if [ ${#block_size[@]} != ${#io_threads[@]} ] || [ ${#block_size[@]} != ${#io_operation[@]} ] || [ ${#block_size[@]} != ${#files_io[@]} ] || [ ${#block_size[@]} != ${#io_rate[@]} ]; then
	    echo "$error received less values then expected please check your settings"
	    echo "received ${#block_size[@]} params for BLOCK_SIZES"
	    echo "received ${#io_threads[@]} params for IO_THREADS"
	    echo "received ${#io_operation[@]} params for IO_OPERATIONS"
	    echo "received ${#files_io[@]} params for FILES_IO"
	    echo "received ${#io_rate[@]} params for IO_RATE"
	    should_exit=1
	fi

    }

    check_dbs_settings(){
	for ((r=0; r < ${#block_size[@]} ; r++)); do
	    for ((y=0; y < ${#dbs_patterns[@]} ; y++)); do
		if [ "${block_size[$r],,}" = "${dbs_patterns[$y],,}" ]; then
		    if [ "${io_operation[$r],,}" != "${block_size[$r],,}" ]; then 
			echo "$error \"${block_size[$r]}\" was requested in cell number ${r} for BLOCK_SIZE but recived a value of \"${io_operation[$r]}\" for IO_OPERATION"
			should_exit=1
	  	    fi
		    if [ "${files_io[$r],,}" != "${block_size[$r],,}" ] ; then
			echo "$error \"${block_size[$r]}\" was requested in cell number ${r} for FILES_IO but recived a value of \"${files_io[$r]}\" for FILES_IO"
			should_exit=1
		    fi
		fi

	    done
	done
    }


    check_io_rate(){
	re='^[0-9]+$'
	for ((r=0; r < ${#io_rate[@]} ; r++)); do
	    if [[ ! ${io_rate[$r]} =~ $re ]] && [[ ${io_rate[$r],,} != "max" ]]; then
		echo "$error value  \"${io_rate[$r],,}\" at cell num ${r} is illegal value for IO_RATE"
		should_exit=1
            fi
	done
    }


    check_run_fillup(){
        if [[ "${run_fillup,,}" != yes ]] && [[ "${run_fillup,,}" != no ]]; then 
	    echo "$erro value of  \"${run_fillup}\" is illegal value for RUN_FILLUP"
	    should_exit=1 ; fi
    }

    did_check_pass(){
	if [[ "${should_exit}" -eq 1 ]]; then exit ; fi
    }

    check_matching_values
    check_dbs_settings
    check_io_rate
    check_run_fillup
    #did_check_pass
}

start_run(){
    generate_workload_config > ${tmp_test_file}
    /./vdbench/vdbench -c -f ${tmp_test_file} -o /tmp > /dev/null #2>&1
    /./vdbench/vdbench parseflat -i /tmp/flatfile.html -o /tmp/results.csv -c Run Xfersize Threads Reqrate Rate Rate_std Rate_max Resp Resp_std Resp_max MB/sec MB_read MB_write Read_rate Read_rate_std Read_rate_max Read_resp Read_resp_std Read_resp_max Write_rate Write_rate_std Write_rate_max Write_resp Write_resp_std Write_resp_max Mkdir_rate Mkdir_rate_std Mkdir_rate_max Mkdir_resp Mkdir_resp_std Mkdir_resp_max Rmdir_rate Rmdir_rate_std Rmdir_rate_max Rmdir_resp Rmdir_resp_std Rmdir_resp_max Create_rate Create_rate_std Create_rate_max Create_resp Create_resp_std Create_resp_max Open_rate Open_rate_std Open_rate_max Open_resp Open_resp_std Open_resp_max Close_rate Close_rate_std Close_rate_max Close_resp Close_resp_std Close_resp_max Delete_rate Delete_rate_std Delete_rate_max Delete_resp Delete_resp_std Delete_resp_max Getattr_rate Getattr_rate_std Getattr_rate_max Getattr_resp Getattr_resp_std Getattr_resp_max Setattr_rate Setattr_rate_std Setattr_rate_max Setattr_resp Setattr_resp_std Setattr_resp_max Access_rate Access_rate_std Access_rate_max Access_resp Access_resp_std Access_resp_max Compratio Dedupratio cpu_used cpu_user cpu_kernel cpu_wait cpu_idle -a > /dev/null 2>&1
    cat /tmp/results.csv|grep -v format_for
}

get_tests_parms_from_env
test_user_settings
start_run
echo ${wd_list[$r]}
