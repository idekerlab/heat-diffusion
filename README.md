heat-diffusion
==============

<img align="right" height="300" src="http://www.cytoscape.org/images/logo/cy3logoOrange.svg">

---

A RESTful service that finds network neighborhoods in a larger network relevant to an initial set of nodes of interest. It works by propagating the node set across the network in a process analogous to heat diffusing across a conductive medium. A typical application would be discovering network mechanisms from hits in a screen or differential expression analysis. More generally this service is applicable for paring a larger network to a smaller, more manageable one based on known nodes of interest. For details on the process of heat diffusion see the manuscript "Network propagation in the Cytoscape Cyberinfrastructure. Carlin DE et al. Submitted to PLoS Computational Biology.

---

heat-diffusion is a [cxmate service](https://github.com/cxmate/cxmate) 
## Sample Jupyter Notebook
Please see the jupyter notebook (demo.ipynb) in the repository for an example interaction with the service. 

## Sample Usage
Assuming heat-diffusion is running http://v3.heat-diffusion.cytoscape.io on port 80, a call via curl might look like:

```bash
curl -X POST -H "Content-Type: application/json" -d "@my_network.cx" -o "my_network.result.cx" "http://v3.heat-diffusion.cytoscape.io:80?time=0.5"
```

my_network.cx must be a CX network containing the nodes, edges and nodeAttributes aspects, as described in **Request Body** below. The result will be a CX network containing node heats and ranks, as described in **Response Body** below. (For convenience, there is a sample my_network.cx and corresponding my_network.result.cx in this repository.)

## Endpoint: POST /
This endpoint diffuses heat in CX network and returns a new network representing the results of the diffusion.

### Query String Parameters

| Name                  | Default Value      | Description                                                                |
|:--------------------- |:------------------ |:-------------------------------------------------------------------------- |
| time                  | 0.1                | The upper bound on the exponential multiplication performed by diffusion   |
| normalize_laplacian   | False              | If True, will create a normalized laplacian matrix for diffusion           | 
| input_attribute_name  | "diffusion_input"  | The key diffusion will use to search for heats in the node attributes with |
| output_attribute_name | "diffusion_output" | Will be the prefix of the _rank and _heat attriubtes created by diffusion  |  

### Request Body `<application/json>`
The body of the request must be a CX network containing the nodes, edges, and nodeAttributes aspects. There must exist at least one nodeAttribute with a key name that matches the `input_attribute_name` parameter and holds a double, which will be interepreted as the heat of that node. (This condition can be minimally fulfilled by omitting the `input_attribute_name` parameter, and having at least one node with an attribute named `diffusion_input` with value 1.0.)

All nodes that do not have this nodeAttribute set will be treated as having zero heat. 

### Response Body `<application/json>`
The response body will contain a CX network containing the nodes, edges, and nodeAttributes aspects. Each node will have two associated attributes, `output_attribute_name`\_rank and `output_attribute_name`\_heat where `output_attribute_name` can be set via the query string parameters (e.g., diffusion_output_rank and diffusion_output_heat). The \_heat attribute will contain the heat of the node after diffusion. The \_rank attribute will have the rank of the node relative to the heats of all other nodes in the network, starting with 0 as the hottest node.

Note that while \_rank and \_heat attributes will be returned for each node in the CX network, attributes present in the input network and not related to heat_diffusion are not guaranteed to be returned.

Running Locally with Docker
---------------------------
A shell script file is included in the repository for local deployments of the service with Docker. Docker is a prerequisites to deploying locally, and are available on [Docker's homepage](https://www.docker.com/)(select your platform under the Get Docker Menu bar entry and follow the installation instructions). Once Docker is installed, you should be able to open a Command Prompt or Terminal and get your docker version with `docker --version` to verify the installation succeeded.

After installing Docker, make sure your shell's working directory is inside of the heat-diffusion repositories top level directory. On a Unix system this might look like: 

```
git clone https://github.com/idekerlab/heat-diffusion && cd heat-diffusion
```

 Run `./scripts/deploy.sh` or `./scripts/deploy.bat` on Windows (make sure you have permissions to execute the script). This will build heat-diffusion locally using Docker, deploy heat-diffusion and it's dependancies locally, and make heat-diffusion callable via localhost:80. When you're done, run `docker container stop heat-diffusion cxmate && docker container rm heat-diffusion cxmate` in the same directory to stop and remove heat-diffusion and its dependancies.

Contributors
------------

We welcome all contributions via Github pull requests. We also encourage the filing of bugs and features requests via the Github [issue tracker](https://github.com/idekerlab/heat-diffusion/issues/new). For general questions please [send us an email](edsage@ucsd.edu).

License
-------

heat-diffusion is MIT licensed and a product of the [Cytoscape Consortium](http://www.cytoscapeconsortium.org).

Please see the [License](https://github.com/cxmate/cxmate/blob/master/LICENSE) file for details.

## Running Locally with Docker

While heat-diffusion is available as a web-based service, there are times when it may be more convenient to run
the service on your local workstation. To accommodate this, we provide instructions for downloading a Docker image
and executing it.

Docker is a prerequisite to your local deployment, and is available on [Docker's homepage](https://www.docker.com/) -- select your platform under the Get Docker Menu bar entry and follow the installation instructions. Once Docker is installed, open your system's shell (i.e., Command Prompt or Terminal) and verify that the installation succeeded by using the `docker --version` command.

After installing Docker, make sure your shell's working directory is inside of the heat-diffusion repository's top level directory: 

```
git clone https://github.com/idekerlab/heat-diffusion && cd heat-diffusion
```

Run the deployment script (`./scripts/deploy.sh` for Mac/Linux, `./scripts/deploy.bat` for Windows) -- you may need administrator
privileges for this. The script builds the heat-diffusion service locally using Docker, deploys heat-diffusion and its dependancies locally, and makes heat-diffusion callable via localhost:80. To test this, use curl as described in the Sample Usage section above,
but use http://localhost:80 in place of the standard service web address.

```bash
curl -X POST -H "Content-Type: application/json" -d "@my_network.cx" -o "my_network.result.cx" "http://localhost:80?time=0.5"
```

When you're done, run `docker container stop heat-diffusion cxmate && docker container rm heat-diffusion cxmate` in the same directory to stop and remove heat-diffusion and its dependencies.
