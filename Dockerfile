FROM public.ecr.aws/lambda/python:3.9-arm64

COPY app/ ${LAMBDA_TASK_ROOT}
COPY pyproject.toml ${LAMBDA_TASK_ROOT}

RUN pip3 install poetry
RUN poetry export -f requirements.txt --without-hashes --output "${LAMBDA_TASK_ROOT}/requirements.txt"
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD ["main.handler"]