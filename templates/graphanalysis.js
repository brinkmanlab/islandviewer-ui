var graph = {{ json_str|safe }};
var g = new dagreD3.graphlib.Graph().setGraph({});

var name_substitutions = {Virulence: 'Annotating Genes',
	Summary: 'Validating Pipeline',
	Sigi: 'SIGI-HMM',
	Dimob: 'IslandPath-DIMOB',
	Islander: 'Islander',
	ContigAligner: 'Contig Rearranger'};

var nodes = graph['nodes'];
var node_labels = {};
for(node in nodes) {
	var nodelabel = nodes[node]['name'];
	node_labels[nodelabel] = true;
	if('undefined' !== typeof(name_substitutions[nodelabel])) {
		nodelabel = name_substitutions[nodelabel];
	}
	g.setNode(nodes[node]['name'], {label: nodelabel, class: nodes[node]['status']});
}
var edges = graph['edges'];
for(edge in edges) {
	var tasks = edges[edge]['nexttask'].split(',');
	for(e in tasks) {
            // If the next task doesn't actually exist in the graph, don't try to add it
	    if('undefined' == typeof node_labels[tasks[e]]) {
	      continue;
            }
	    params = {class: edges[edge]['status'], lineInterpolate: 'basis'};
	    if('undefined' !== edges[edge]['status'] && edges[edge]['status'] == 'FAILED') {
		params['style'] = 'stroke: red; fill: none; stroke-dasharray: 5, 5;';
		params['arrowheadStyle'] = 'fill: red; stroke: none;';
	    }
	    g.setEdge(edges[edge]['name'], tasks[e], params);
	    //	    g.setEdge(edges[edge]['name'], tasks[e], {class: edges[edge]['status'], lineInterpolate: 'basis'});
	}
}

var render = new dagreD3.render();
//var oldDrawNodes = renderer.drawNodes();
//renderer.drawNodes(function(graph, root) {
//   var svgNodes = oldDrawNodes(graph, root);
//    svgNodes.each(function(u) { d3.select(this).classed(graph.node(u).nodeclass, true); });
//    return svgNodes;
//  });

var layout = render(d3.select("svg g"), g);
//  d3.select("svg")
//    .attr("width", layout.graph().width + 40)
//    .attr("height", layout.graph().height + 40);

