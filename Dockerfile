# Use an official Python runtime as a base image
FROM python:3.9-slim

# Expose the port to run it
ENV LISTEN_PORT=5000
EXPOSE 5000

# Preset the volume
VOLUME /dash_plotly_QC_scRNA/./data

LABEL Maintainer="arts-of-coding"

WORKDIR /dash_plotly_QC_scRNA

COPY ./dash_plotly_QC_scRNA/requirements.txt ./
RUN pip install --requirement ./requirements.txt

COPY ./dash_plotly_QC_scRNA/dash_qc_scrna/dash_plotly_QC_scRNA.py ./

# How the docker app will run
CMD [ "python", "./dash_plotly_QC_scRNA.py"]