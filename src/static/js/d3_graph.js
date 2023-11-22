function create_graph(topology) {
    // Convert adjacency matrix to nodes and links
    let nodes = topology.devices.map(d => ({id: d.key_name,em:d.emulator_id}));
    let uniqueItems = [...new Set(nodes.map(d=> {return d.em}))]
    console.log(uniqueItems)
    var colors = d3.scaleOrdinal().domain(uniqueItems).range(["gold", "blue", "green", "yellow", "black", "grey", "darkgreen", "pink", "brown", "slateblue", "grey1", "orange"])
  
    function find_node(key_name) {
        for(const node of nodes) {
            console.log(node)
            if (node.id === key_name){
                console.log("found:", nodes)
                return node
            }
        }
        window.alert("node not not found")
    }
    let links = topology.connections.map(d => ({source: find_node(d.source), target: find_node(d.target)}))
    console.log(nodes)
    console.log(links)

    
    d3.select('#graph').selectAll("*").remove()

    // Set up the SVG
    let width = '600';
    let height = '600';
    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    window.addEventListener('resize', () => {
        console.log('resize');
        svg.attr("width", window.innerWidth)
            .attr("height", window.innerHeight);
    });

    // Create the force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).distance(100))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

    // function boundingBoxForce() {
    //     return function() {
    //         nodes.forEach(node => {
    //             console.log(node)
    //             if(!node.radius){
    //                 node.radius = 5
    //             }
    //             node.x = Math.max(node.radius, Math.min(width - node.radius, node.x));
    //             node.y = Math.max(node.radius, Math.min(height - node.radius, node.y));
    //         });
    //     }
    // }
    
    // // Assuming 'simulation' is your d3.forceSimulation
    // simulation.force('bounds', boundingBoxForce());

    // Draw lines for the links
    const link = svg.append('g')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .selectAll('line')
        .data(links)
        .join('line');

    function on_node_click(a, b, c) {
        console.log("clicked node:", a, b, c)
        console.log("clicked node:", b.id)
    }
    // Draw circles for the nodes
    const node = svg.append('g')
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .selectAll('circle')
        .data(nodes)
        .join('circle')
        .attr('r', 5)
        .attr('fill',function(d){return colors(d.em)})
        .on('click', on_node_click)

    // Update positions each tick
    function ticked() {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    }

    // Optionally, add drag behavior
    node.call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

function updateGraph(newMatrix) {
    // Convert the new adjacency matrix to nodes and links
    let newNodes = newMatrix.map((_, i) => ({ id: i }));
    let newLinks = [];

    newMatrix.forEach((row, i) => {
        row.forEach((cell, j) => {
            if (cell === 1 && i < j) { // Avoid duplicates
                newLinks.push({ source: i, target: j });
            }
        });
    });

    // Update the nodes and links data
    nodes = newNodes;
    links = newLinks;

    // Restart the simulation with new data
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    simulation.alpha(1).restart();

    // Re-bind the data to the node and link elements
    link = link.data(links, d => d.source.id + "-" + d.target.id);
    link.exit().remove();
    link.enter().append('line')
        // additional attributes for new links

    node = node.data(nodes, d => d.id);
    node.exit().remove();
    node.enter().append('circle')
}

function new_adjacency_matrix() {
    fetch('/current_topology')
        .then(response => {
            if (!response.ok) {
                window.alert(response.status, response.body())
                return {devices: [{key_name: "a"}, {key_name: "b"}], connections: [{source: "a", target: "b"}]}
            }
            return response.json()
        })
        .then(topology => {
            console.log(topology)
            create_graph(topology)
        });
}
