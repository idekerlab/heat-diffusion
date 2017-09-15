heat-diffusion
==============

<img align="right" height="300" src="http://www.cytoscape.org/images/logo/cy3logoOrange.svg">

---

A service that finds network neighborhoods in a larger network relevant to an initial set of nodes of interest. It works by propagating the node set across the network in a process analogous to heat diffusing across a conductive medium. A typical application would be discovering network mechanisms from hits in a screen or differential expression analysis. More generally this service is applicable for paring a larger network to a smaller, more manageable one based on known nodes of interest. For details on the process of heat diffusion see the manuscript "Network propagation in the Cytoscape Cyberinfrastructure. Carlin DE et al. Submitted to PLoS Computational Biology.

---

heat-diffusion is a [cxmate service](https://github.com/cxmate/cxmate)

## POST /
This endpoint diffuses heat in CX network and returns a new network representing the results of the diffusion.

# BD: Can you provide a sample call and sample results?

### Query String Parameters

| Name                  | Default Value      | Description                                                                |
|:--------------------- |:------------------ |:-------------------------------------------------------------------------- |
| time                  | 0.1                | The upper bound on the exponential multiplication performed by diffusion   |
| normalize_laplacian   | False              | If True, will create a normalized laplacian matrix for diffusion           | 
| input_attribute_name  | "diffusion_input"  | The key diffusion will use to search for heats in the node attributes with |
| output_attribute_name | "diffusion_output" | Will be the prefix of the _rank and _heat attriubtes created by diffusion  |  

# BD: What is the range of values "time" can take? Can you use a paragraph to explain what a CX network is, how to build one, and what to do with one when it's returned? Best to do this before "Query String Parameters" so reader has context. Good to distinguish between body and parameters, and identify as both being necessary for the call.

### Request Body `<application/json>`
The body of the request must be a CX container containing the nodes, edges, and nodeAttributes aspects. There must exist at least one nodeAttribute with a key name that matches the `input_attribute_name` parameter and holds a double, which will be intereprested as the heat of that node. All nodes that do not have this nodeAttribute set will be treated as having zero heat.

### Response Body `<application/json>`
THe reponse body will contain a CX container containing the nodes, edges, and nodeAttributes aspects. Each node will have two associated attributes, `output_attribute_name`\_rank and `output_attribute_name`\_heat where `output_attribute_name` can be set via the query string parameters. The \_heat attribute will contain the heat of the node after diffusion, the \_rank will have the rank of the node relative to the heats of all other nodes in the network, starting with 0 as the hottest node.

# BD: Please add a Team Members section, with e-mails for the team members. Need to give credit and also provide a human-human linkage.

Contributors
------------

We welcome all contributions via Github pull requests. We also encourage the filing of bugs and features requests via the Github [issue tracker](https://github.com/idekerlab/heat-diffusion/issues/new). For general questions please [send us an email](eric.david.sage@gmail.com).

License
-------

heat-diffusion is MIT licensed and a product of the [Cytoscape Consortium](http://www.cytoscapeconsortium.org).

Please see the [License](https://github.com/cxmate/cxmate/blob/master/LICENSE) file for details.
