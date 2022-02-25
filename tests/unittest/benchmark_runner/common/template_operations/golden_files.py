
import difflib
import filecmp
import os
import shutil
import tempfile
from benchmark_runner.main.environment_variables import environment_variables
from benchmark_runner.common.template_operations.template_operations import TemplateOperations
from tests.unittest.benchmark_runner.common.template_operations.golden_files_exceptions import GoldenFileCheckFailed


class GoldenFiles:
    """Generate golden files for regression testing"""

    def __init__(self):
        self.__file_path = os.path.join(f'{os.path.dirname(os.path.realpath(__file__))}', 'golden_files')
        environment_variables.environment_variables_dict['elasticsearch'] = 'elasticsearch.example.com'
        environment_variables.environment_variables_dict['elasticsearch_port'] = '9999'
        environment_variables.environment_variables_dict['elasticsearch_url'] = 'http://elasticsearch.example.com:gol9999'
        environment_variables.environment_variables_dict['pin'] = 'True'
        environment_variables.environment_variables_dict['pin_node1'] = 'pin-node-1'
        environment_variables.environment_variables_dict['pin_node2'] = 'pin-node-2'
        environment_variables.environment_variables_dict['prom_token_override'] = 'fake_prom_token'
        environment_variables.environment_variables_dict['uuid'] = 'deadbeef-0123-3210-cdef-01234567890abcdef'
        environment_variables.environment_variables_dict['trunc_uuid'] = environment_variables.environment_variables_dict['uuid'].split('-')[0]

    def __clear_directory_yaml(self, dir):
        if os.path.isdir(dir):
            for file in os.listdir(dir):
                if file.endswith('.yaml'):
                    os.remove(os.path.join(dir, file))

    def __generate_yaml_dir_name(self, run_type: str, workload: str, odf_pvc: str, dest: str=None):
        if dest is None:
            dest = self.__file_path
        return os.path.join(dest, f'{run_type}_{workload}_ODF_PVC_{odf_pvc}')

    def __copy_yaml_files_to_dir(self, src: str, dest: str):
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.mkdir(dest)
        if os.path.isdir(src):
            for file in os.listdir(src):
                if file.endswith('.yaml'):
                    with open(os.path.join(src, file), 'r') as r:
                        with open(os.path.join(dest, file), 'w') as w:
                            w.write(r.read())

    def __generate_golden_yaml_files__(self, dest: str=None):
        if not dest:
            dest = self.__file_path
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.mkdir(dest)
        for odf_pvc in 'True', 'False':
            environment_variables.environment_variables_dict['odf_pvc'] = odf_pvc
            for run_type in environment_variables.run_types_list:
                environment_variables.environment_variables_dict['run_type'] = run_type
                for workload in environment_variables.workloads_list:
                    environment_variables.environment_variables_dict['namespace'] = environment_variables.get_workload_namespace(workload)
                    template = TemplateOperations(workload)
                    srcdir = template.get_current_run_path()
                    self.__clear_directory_yaml(srcdir)
                    destdir = self.__generate_yaml_dir_name(run_type=run_type, workload=workload, odf_pvc=odf_pvc, dest=dest)
                    template.generate_yamls()
                    self.__copy_yaml_files_to_dir(src=srcdir, dest=destdir)
                    self.__clear_directory_yaml(srcdir)

    # From https://stackoverflow.com/questions/4187564/recursively-compare-two-directories-to-ensure-they-have-the-same-files-and-subdi
    def __compare_tree__(self, root1, root2, subdir: str):
        """
        Compare two directories recursively. Files in each directory are
        considered to be equal if their names and contents are equal.

        @param dir1: First directory path
        @param dir2: Second directory path

        @return: [left_only, right_only, diff_files, funny_files]
       """

        def canon_list(subdir: str, files: list):
            return list(map(lambda f: os.path.join(subdir, f), files))

        dir1 = os.path.join(root1, subdir)
        dir2 = os.path.join(root2, subdir)
        dirs_cmp = filecmp.dircmp(dir1, dir2)
        left_only = canon_list(subdir, dirs_cmp.left_only)
        right_only = canon_list(subdir, dirs_cmp.right_only)
        diff_files = []
        funny_files = []

        (_, mismatch, errors) =  filecmp.cmpfiles(dir1, dir2, dirs_cmp.common_files, shallow=False)
        diff_files.extend(canon_list(subdir, mismatch))
        funny_files.extend(canon_list(subdir, errors))

        for common_dir in dirs_cmp.common_dirs:
            new_subdir = os.path.join(subdir, common_dir)
            (sub_left_only, sub_right_only, sub_diff_files, sub_funny_files) = self.__compare_tree__(root1, root2, new_subdir)
            left_only.extend(sub_left_only)
            right_only.extend(sub_right_only)
            diff_files.extend(sub_diff_files)
            funny_files.extend(sub_funny_files)
        return (left_only, right_only, diff_files, funny_files)

    def __compare_golden_yaml_files__(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.__generate_golden_yaml_files__(dest=tmpdir)
            (left_only, right_only, diff_files, funny_files) = self.__compare_tree__(self.__file_path, tmpdir, '.')
            for filename in diff_files:
                print(f'\n{filename}:')
                golden_file = os.path.join(self.__file_path, filename)
                comparison_file = os.path.join(tmpdir, filename)
                with open(golden_file) as golden:
                    golden_text = golden.readlines()
                with open(comparison_file) as comparison:
                    comparison_text = comparison.readlines()
                for line in difflib.unified_diff(golden_text, comparison_text, fromfile=golden_file, tofile=comparison_file, lineterm=''):
                    print(line, end='')
            if len(left_only) > 0 or len(right_only) > 0 or len(diff_files) > 0 or len(funny_files) > 0:
                raise GoldenFileCheckFailed(miscompare=diff_files, missing=left_only, unexpected=right_only, cannot_compare=funny_files)
        return True

    def generate_golden_files(self):
        self.__generate_golden_yaml_files__()

    def compare_golden_files(self):
        return self.__compare_golden_yaml_files__()
