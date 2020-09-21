FROM sparrowdata/backend

RUN apk add --no-cache make

WORKDIR /docs

COPY ./requirements.txt /docs/requirements.txt
RUN pip install --no-cache -r /docs/requirements.txt

ENV BACKEND_ROOT=/app
ENV SPARROW_SECRET_KEY=docs

COPY ./ /docs/

CMD make html
