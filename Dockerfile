FROM  python:2

RUN pip install grpcio-tools networkx futures scipy numpy cxmate

COPY . .

CMD [ "python", "heat_diffusion_service.py" ]
