# Generate graphs of interest from the output of sesearch

from typing import Dict, List


class allow:
    filename: str
    graph: Dict[str, List]
    chr_graph: Dict[str, List]

    def __init__(self, filename: str) -> None:
        try:
            print(f"[*] Attempting to open {filename}")
            fd = open(filename, "r")
        except OSError as e:
            print(f"  [!] open on {filename} failed: OSError occurred: {e}")
        print(f"  [+] opened {filename}")
        self.filename = filename
        self.graph = dict()
        self.chr_graph = dict()
        self.untrusted = dict()
        self.untrusted_open = dict()
        self.parse()
        self.base = """<!DOCTYPE html>
<meta charset="utf-8">
<title>Adjacency Graph</title>
<svg width="100%" height="100%"  style="border:1px solid pink">
<style>
  body { background: #1e1e1e; margin: 0; overflow: hidden; }
  text { fill: white; font: 12px sans-serif; pointer-events: none; }
  line { stroke: #88cc88; stroke-width: 1.5px; marker-end: url(#arrow); }
  circle { fill: #2d3e50; stroke: #88cc88; stroke-width: 2px; }
  .label { fill: #ffcc66; font-size: 10px; }
</style>
<body>
<svg width="100%" height="100%"></svg>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
{
let nodes = __NODES__
let links = __LINKS__

let width = window.innerWidth;
let height = window.innerHeight;

let svg = d3.select("svg")
  .attr("viewBox", [0, 0, width, height])
  .call(d3.zoom().on("zoom", (event) => {
    g.attr("transform", event.transform);
  }));

let g = svg.append("g");

g.append("defs").append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 10 10")
  .attr("refX", 30)
  .attr("refY", 0)
  .attr("markerWidth", 6)
  .attr("markerHeight", 6)
  .attr("orient", "auto")
  .append("path")
  .attr("d", "M0,-5L10,0L0,5")
  .attr("fill", "pink");

let simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(230))
  .force("charge", d3.forceManyBody().strength(-900))
  .force("center", d3.forceCenter(width / 2, height / 2));

let link = g.append("g")
  .selectAll("path")
  .data(links.map((d, i) => ({ ...d, id: "link" + i })))   // add a unique id
  .join("path")
    .attr("id", d => d.id)          // <—— id that <textPath> will reference
    .attr("fill", "none")
    .attr("stroke-width", 1.5)
    .attr("stroke", d => d.label === "open" ? "#ff6666" : "#88cc88")
    .attr("marker-end", "url(#arrow)");

let edgeLabels = g.append("g")
  .selectAll("text")
  .data(links)
  .join("text")
    .attr("class", "edge-label")
  .append("textPath")
    .attr("href", (d, i) => "#link" + i)   // tie to the path above
    .attr("startOffset", "50%")            // centre the text
    .attr("text-anchor", "middle")
    .text(d => d.label ?? "");         

g.selectAll(".edge-label textPath")
  .style("pointer-events", "none");

simulation.on("tick", () => {
  link.attr("d", d => `M${d.source.x},${d.source.y}L${d.target.x},${d.target.y}`);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);

  labels
    .attr("x", d => d.x)
    .attr("y", d => d.y);
});


let node = g.append("g")
  .selectAll("circle")
  .data(nodes)
  .join("circle")
  .attr("r", 18)
  .call(drag(simulation));

let labels = g.append("g")
  .selectAll("text")
  .data(nodes)
  .join("text")
  .text(d => d.id);

function drag(simulation) {
  return d3.drag()
    .on("start", (event, d) => {
      if (!event.active) simulation.alphaTarget(3).restart();
      d.fx = d.x;
      d.fy = d.y;
    })
    .on("drag", (event, d) => {
      d.fx = event.x;
      d.fy = event.y;
    })
    .on("end", (event, d) => {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    });
}

simulation.on("tick", () => {
  link.attr("d", d => `M${d.source.x},${d.source.y}L${d.target.x},${d.target.y}`);

  node
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);

  labels
    .attr("x", d => d.x)
    .attr("y", d => d.y);
});
}
</script>"""


    # construct a graph from self.filename
    def parse(self):
      print("[*] Parsing.")
      try:
        fd = open(self.filename, "r")
      except OSError:
        print(f"  [!] Failed to open {self.filename}")
        return None
      for line in fd:
        tokens = line.replace("\n", "").replace(";", "").split(" ")
        if len(tokens) < 4:
          print(f"  [!] Unexpected length of tokens {tokens}")
          continue
        ruleTy = tokens[0]
        source = tokens[1]
        destination = tokens[2]
        permission = "".join(tokens[3:])

        if source not in self.graph.keys():
          self.graph[source] = [(destination, permission)]
        else:
          self.graph[source].append((destination, permission))
        if destination not in self.graph.keys():
            self.graph[destination] = []
        if ":chr_file" in source or ":chr_file" in destination:
          if source not in self.chr_graph.keys():
            self.chr_graph[source] = [(destination, permission)]
          else:
            self.chr_graph[source].append((destination, permission))
        if "untrusted_app" == source or "untrusted_app_all" == source:
          if source not in self.untrusted.keys():
            self.untrusted[source] = [(destination, permission)]
          else:
            self.untrusted[source].append((destination, permission))
          if "open" in permission:
            if source not in self.untrusted_open.keys():
                self.untrusted_open[source] = [(destination, permission)]
            else:
                self.untrusted_open[source].append((destination, permission))
 
      print(f"graph: {len(list(self.graph.keys()))}")
      print(f"chr graph: {len(list(self.chr_graph.keys()))}")
      print(f"untrusted graph: {len(list(self.untrusted.keys()))}")
      print(f"untrusted open graph: {len(list(self.untrusted_open.keys()))}")

    # generate a d3 javascript representation
    def show(self, graph):
        # replace nodes
        seen_nodes = set()
        seen_edges = set()
        nodes = "["
        for node in graph.keys():
            if str(node) not in seen_nodes:
                nodes += "{\"id\": \"" + str(node) + "\"}, "
                seen_nodes.add(str(node))
            for target in graph[node]:
                if str(target[0]) not in seen_nodes:
                    nodes += "{\"id\": \"" + str(target[0]) + "\"}, "
                    seen_nodes.add(str(target[0]))
        nodes = nodes[:-2]
        nodes += "];"
        base = self.base.replace("__NODES__", nodes)

        # replace links (edges)
        links = "["
        for node in graph.keys():
            for edge in graph[node]:
              dest = edge[0]
              perm = edge[1]
              # add source
              links += "{\"source\": \"" + str(node) + "\", "
              # add destination
              links += "\"target\": \"" + str(dest) + "\", "
              links += "\"label\": \"\"}, "
        links = links[:-2]
        links += "];"
        return base.replace("__LINKS__", links)


if __name__ == "__main__":
    policy = allow("allow_16")
    html = policy.show(policy.graph)
    chr = policy.show(policy.chr_graph)
    untrusted = policy.show(policy.untrusted)
    untrusted_open = policy.show(policy.untrusted_open)
    # all allow nodes/edges
    with open("all.html", "a") as wl:
        wl.write(html)
    # all nodes involving character devices
    with open("chr.html", "a") as wl:
        wl.write(chr)
    # all nodes/edges involving untrusted context
    with open("untrusted.html", "a") as wl:
        wl.write(untrusted)
    # all nodes/edges involving untrusted -> open permission
    with open("untrusted_open.html", "a") as wl:
        wl.write(untrusted_open)

