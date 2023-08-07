# jsonnet/jsonnetfile.lock.json - representing a specific grafonnet version and not latest
apply:
	@cd jsonnet/ && \
		jb install && \
		cd ../ && \
		terraform apply -auto-approve | python3 extract_dashboard.py > dashboard.json
