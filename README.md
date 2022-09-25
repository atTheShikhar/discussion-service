## Installation and Setup

To run the backend service locally:
1. Make sure [Docker](https://www.docker.com/) is installed in your system.
2. `cd` into the `backend` directory, create a `.env` file and add all the variables present in `env.example` file.
4. Run:
```
docker build -t discussion-service:1.0 .
docker run -p 8000:8000 discussion-service:1.0
```

## Documentation
- Backend documentation: [here](BackendDocumentaion.md)