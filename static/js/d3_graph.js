function create_graph(matrix) {
    // Convert adjacency matrix to nodes and links
    let nodes = matrix.map((_, i) => ({ id: i }));
    let links = [];

    matrix.forEach((row, i) => {
        row.forEach((cell, j) => {
            if (cell === 1 && i < j) { // To avoid duplicates
                links.push({ source: i, target: j });
            }
        });
    });

    d3.select('#graph').selectAll("*").remove()

    // Set up the SVG
    const width = '600', height = '600';
    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    // Create the force simulation
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).distance(100))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

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
        .attr('fill', 'blue')
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
    fetch('/new_adjacency_matrix')
        .then(response => {
            if (!response.ok) {
                window.alert(response.status, response.body())
                return [[1,1],[1,1]]
            }
            return response.json()
        })
        .then(matrix => {
            create_graph(matrix)
        });
}
