FROM klakegg/hugo:0.101.0-ext-alpine
CMD [ "serve", "-D", "--bind", "0.0.0.0" ]
ENTRYPOINT [ "hugo" ]
