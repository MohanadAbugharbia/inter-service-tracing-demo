FROM python:3.11-slim AS builder

SHELL [ "/bin/bash", "-c" ]

ENV VIRTUAL_ENV=/opt/bob/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
ENV PYTHONPATH=/opt/bob
ENV POETRY_VERSION=1.8.4


# Create a user and group that will be used to run code
RUN /usr/sbin/addgroup --gid 1000 bob \
    && /usr/sbin/adduser --system --shell /bin/bash --home /var/lib/bob --gid 1000 --uid 1000 bob \
    && /usr/sbin/adduser bob bob\
    && echo 'source /opt/bob/venv/bin/activate' >> /var/lib/bob/.bashrc \
    && mkdir -p /opt/bob \
    && chown -R bob:bob /opt/bob

USER bob

WORKDIR /opt/bob

# Initiate the virtual environment and install the dependencies
ADD --chown=bob:bob pyproject.toml /opt/bob/
ADD --chown=bob:bob poetry.lock /opt/bob/
RUN python -m venv $VIRTUAL_ENV \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry --no-cache install --only main



# Copy the source code and set the owder as bob user
COPY --chown=bob:bob . /opt/bob/

EXPOSE 8000

CMD ["bash", "-c", "source /opt/bob/venv/bin/activate && uvicorn src.app:app --host 0.0.0.0 --port 8000"]
