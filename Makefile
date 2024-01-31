bump:
	bumpver update --patch --no-fetch

bump_minor:
	bumpver update minor --no-fetch

bump_major:
	bumpver update major --no-fetch

bump_beta:
	bumpver update --no-fetch --patch --tag=beta --tag-num

bump_beta_next:
	bumpver update --no-fetch --tag-num --commit

bump_remove_beta_tag:
	bumpver update --no-fetch --tag=final --commit --commit-message="Final release from {old_version} to {new_version}"
