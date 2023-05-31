FROM author/cleanenv:v0.0
WORKDIR ./workbench
COPY . .
EXPOSE 8300
CMD ["gunicorn", "--chdir", "./app", "generateAuthorization:app", "-c", "./app/gunicorn.conf.py", "-t", "8300"]

