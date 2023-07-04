FROM python:3.11-bullseye

ARG _USER="hyper_bump_it"
ARG _UID="1000"
ARG _GID="100"
ARG _SHELL="/bin/bash"


RUN useradd -m -s "${_SHELL}" -N -u "${_UID}" "${_USER}"

ENV USER ${_USER}
ENV UID ${_UID}
ENV GID ${_GID}
ENV HOME /home/${_USER}
ENV PATH "${HOME}/.local/bin/:${PATH}"
ENV PIP_NO_CACHE_DIR "true"


RUN mkdir /app && chown ${UID}:${GID} /app

USER ${_USER}

RUN git config --global user.name "TESTING-${_USER}" && \
    git config --global user.email "TESTING-${_USER}@example.com"

# Create a signing certificate to use for testing. Once the certificate exipires, the image will
# need to be rebuilt.
RUN gpg --quick-generate-key --batch --passphrase '' "TESTING-${_USER} <TESTING-${_USER}@example.com>" default sign 3m

COPY --chown=${UID}:${GID} ./requirements*.txt /app/
WORKDIR /app

RUN pip install -r requirements.txt -r requirements-test.txt -r requirements-docs.txt

CMD bash
