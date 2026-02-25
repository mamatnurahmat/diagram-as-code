# docker build -t newrahmat/diagram .
#docker run --rm -v "$PWD:/app" newrahmat/diagram
docker run --rm -v "$PWD:/app" newrahmat/diagram python topology.py
