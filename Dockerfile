FROM python:3.9.8


RUN apt update && \ 
    apt -y upgrade


WORKDIR /robot

COPY . .

RUN python -m pip install --upgrade pip && \
    pip3 install -r req.txt

RUN echo "Build and run the robot..."

CMD ["python", "-m" ,"robot_main.py"]
