// # contributors: AGRAWASA NROBINSO
function create_graph(topology) {
    let nodes = topology.devices.map(d => ({id: d.key_name, em:d.emulator_id, interface: d.host + ":" + d.port}));
    let uniqueItems = [...new Set(nodes.map(d=> {return d.em}))]
    console.log(uniqueItems)
    var colors = d3.scaleOrdinal().domain(uniqueItems).range(["gold", "blue", "green", "yellow", "black", "grey", "darkgreen", "pink", "brown", "slateblue", "grey1", "orange"])
  
    let width = window.innerWidth;
    let height = window.innerHeight;

    let centralNode = {
        id: "center",
        fx: width / 2,
        fy: height / 2,
    }; // fx and fy fix the node's position
    nodes.push(centralNode);

    function find_node(key_name) {
        for(const node of nodes) {
            if (node.id === key_name){
                return node
            }
        }
        window.alert("node not not found")
    }

    const tooltip = d3.select('body').append('div')
        .attr('class', 'tooltip')
        .style('opacity', 0);


    let links = topology.connections.map(d => ({source: find_node(d.source), target: find_node(d.target)}))
    console.log(nodes)
    console.log(links)

    nodes.forEach(node => {
        if (node.id !== "center") {
            links.push({ source: node, target: centralNode, invisible: true });
        }
    });

    
    d3.select('#graph').selectAll("*").remove()

    const svg = d3.select('#graph')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    window.addEventListener('resize', () => {
        console.log('resize');
        width = window.innerWidth;
        height = window.innerHeight;
        svg.attr("width", width)
            .attr("height", height);

        simulation.force('center', d3.forceCenter(width/2,height/2))
            .alpha(1)
            .restart();
    });

    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).distance(10))
        .force('charge', d3.forceManyBody().strength(-45))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .on('tick', ticked);

    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('stroke', d => d && d.invisible ? 'none' : '#999')
        .attr('stroke-opacity', 0.6);

    function on_node_click(a, b, c) {
        console.log("clicked node:", a, b, c)
        console.log("clicked node:", b.id)
    }

    const node = svg.append('g')
        .attr('stroke', '#fff')
        .attr('stroke-width', 1.5)
        .selectAll('circle')
        .data(nodes.filter(d=>d.id!=='center'))
        .join('circle')
        .attr('r', 5)
        .attr('fill',function(d){return colors(d.em)})
        .on('click', on_node_click)
        .on('mouseover', function(event, d) {
            tooltip.transition()
                .duration(200)
                .style('opacity', .9);
            tooltip.html(d.interface)
                .style('left', (event.pageX) + 'px')
                .style('top', (event.pageY - 28) + 'px');
        })
        .on('mouseout', function(d) {
            tooltip.transition()
                .duration(500)
                .style('opacity', 0);
        });

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

// # contributors: NROBINSO
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


new_adjacency_matrix()