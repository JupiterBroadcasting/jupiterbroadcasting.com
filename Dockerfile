FROM registry.gitlab.com/pages/hugo/hugo_extended:0.101.0
CMD [ "serve", "-D", "--bind", "0.0.0.0" ]
ENTRYPOINT [ "hugo" ]
