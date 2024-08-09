FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    tar \
    python3 \
    python3-pip \
    git \
    wget \
    ca-certificates \
    curl \
    unzip \
    autotools-dev \
    automake \
    build-essential \
    libtool \
    poppler-utils poppler-data \
    ocrmypdf \
    tesseract-ocr tesseract-ocr-jpn libtesseract-dev libleptonica-dev tesseract-ocr-script-jpan tesseract-ocr-script-jpan-vert \
    ghostscript \
    libgl1-mesa-glx \
    libglib2.0-0

# pandocのインストール
RUN wget https://github.com/jgm/pandoc/releases/download/3.3/pandoc-3.3-1-amd64.deb &&\
    apt-get install -y ./pandoc-3.3-1-amd64.deb && \
    rm pandoc-3.3-1-amd64.deb &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# aws-cliのインストール
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" &&\
    unzip awscliv2.zip && \
    ./aws/install -i /usr/local/aws-cli -b /usr/bin


RUN mkdir -p /marker && \
    mkdir -p /usr/share/tessdata && \
    echo "TESSDATA_PREFIX=$(find / -name tessdata -type d | grep tesseract)" > /marker/local.env
ENV TESSDATA_PREFIX=/usr/share/tessdata
RUN echo "source /marker/local.env" >> ~/.bashrc

RUN ln -s /usr/bin/python3 /usr/bin/python
COPY requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash"]
