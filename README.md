heat-diffusion
==============

<img align="right" height="300" src="http://www.cytoscape.org/images/logo/cy3logoOrange.svg">

---

Accepts a network with node heats, and propogates the heat along edges to create a new heat layout. For details see the manuscript "Network propagation in the Cytoscape Cyberinfrastructure. Carlin DE et al. Submitted to PLoS Computational Biology."

---

## POST /
This endpoint diffuses heat in CX network and returns a new network representing the results of the diffusion.

### Query String Parameters

| Name                  | Default Value      | Description                                                                |
| --------------------- |:------------------:|:-------------------------------------------------------------------------- |
| time                  | 0.1                | The upper bound on the exponential multiplication performed by diffusion   |
| normalize_laplacian   | False              | If True, will create a normalized laplacian matrix for diffusion           | 
| input_attribute_name  | "diffusion_input"  | The key diffusion will use to search for heats in the node attributes with |
| output_attribute_name | "diffusion_output" | Will be the prefix of the _rank and _heat attriubtes created by diffusion  |  

### Request Body
The body of the request must be a CX container containing the nodes, edges, and nodeAttributes aspects. There must exist at least one nodeAttribute with a key name that matches the `input_attribute_name` parameter and holds a double, which will be intereprested as the heat of that node. All nodes that do not have this nodeAttribute set will be treated as having zero heat.

### Response Body
THe reponse body will contain a CX container containing the nodes, edges, and nodeAttributes aspects. Each node will have two associated attributes, `output_attribute_name`_rank and `output_attribute_name`_heat where `output_attribute_name` can be set via the query string parameters. The _heat attribute will contain the heat of the node after diffusion, the _rank will have the rank of the node relative to the heats of all other nodes in the network, starting with 0 as the hottest node.
