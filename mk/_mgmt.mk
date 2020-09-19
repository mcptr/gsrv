tmuxp: assert-venv
	tmuxp load tmuxp.yaml


status: git-status


git-status:
	git status -s --ahead-behind --show-stash -b
