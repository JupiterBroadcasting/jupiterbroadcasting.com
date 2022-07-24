FROM registry.gitlab.com/pages/hugo/hugo_extended:latest
CMD [ "serve", "-D", "--bind", "0.0.0.0" ]
ENTRYPOINT [ "hugo" ]
