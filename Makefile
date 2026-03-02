hooks:
	sh scripts/install-hooks.sh

deploy:
	sh scripts/deploy.sh

.PHONY: hooks deploy
