
FROM python:3.11-slim
WORKDIR /app
COPY . /app/
RUN chmod +x esegui_leas_plc.sh
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV DOTENV=.env
CMD ["./esegui_leas_plc.sh"]