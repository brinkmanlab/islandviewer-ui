function MultiVis(targetNode){
    const SEQUENCEHEIGHT = 50;

    this.container = d3.select(targetNode);
    this.sequences = [];
    this.backbone = new Backbone();

    this.addSequence = function (sequenceId, sequenceSize){
        seq = new Sequence(sequenceId, sequenceSize);
        this.sequences.push(seq);

        return seq;
    };

    this.getLargestSequenceSize = function(){
        var largestSize=0;
        for (var i = 0; i<this.sequences.length; i++){
            if (this.sequences[i].getSequenceSize()>largestSize){
                largestSize = this.sequences[i].getSequenceSize();
            }
        }
        return largestSize;
    };

    this.containerWidth = function() {
        return this.container.node().getBoundingClientRect().width;
    };

    this.containerHeight = function() {
        return this.sequences.length*SEQUENCEHEIGHT;
    };

    this.render = function (){
        var scale = d3.scale.linear().domain([0,this.getLargestSequenceSize()]).range([0,this.containerWidth()]);

        //Add the SVG
        var svg = this.container.append("svg")
            .attr("width",this.containerWidth())
            .attr("height",this.containerHeight());

        //Draw Homologous Region Lines
        var lines = [];

        for (var i=0; i<this.sequences.length-1; i++){
            var seqlines = svg.append("g");
            var homologousRegions = (this.backbone.retrieveHomologousRegions(i,i+1));

            for (var j=0;j<homologousRegions.length;j++){
                var homolousRegion = seqlines.append("g");

                //Start Of Homologous Region
                homolousRegion.append("line")
                    .style("stroke","black")
                    .attr("x1",scale(homologousRegions[j].start1))
                    .attr("y1",SEQUENCEHEIGHT*i)
                    .attr("x2",scale(homologousRegions[j].start2))
                    .attr("y2",SEQUENCEHEIGHT*(i+1));

                //End of Homologous Region
                homolousRegion.append("line")
                    .style("stroke","black")
                    .attr("x1",scale(homologousRegions[j].end1))
                    .attr("y1",SEQUENCEHEIGHT*i)
                    .attr("x2",scale(homologousRegions[j].end2))
                    .attr("y2",SEQUENCEHEIGHT*(i+1));

                //Build Shaded Polygon For Homologous Region
                var points = scale(homologousRegions[j].start1)+","+SEQUENCEHEIGHT*i+" ";
                points += scale(homologousRegions[j].end1)+","+SEQUENCEHEIGHT*i+" ";
                points += scale(homologousRegions[j].end2)+","+SEQUENCEHEIGHT*(i+1)+" ";
                points += scale(homologousRegions[j].start2)+","+SEQUENCEHEIGHT*(i+1)+" ";

                homolousRegion.append("polygon")
                    .attr("points",points)
                    .attr("stroke","#808080")
                    .attr("stroke-width",1)
                    .attr("fill","#C0C0C0");
            }
        }

        //Add the sequences to the SVG
        var seq = svg.selectAll("sequences")
            .data(this.sequences)
            .enter()
            .append("g")
            .append("rect")

        //Modify the attributes of the sequences on the SVG
        seq.attr("x",0)
            .attr("y",function (d, i){
                return (i*50)+"px";
            })
            .attr("height", 2)
            .attr("width", function (d){
                return scale(d.getSequenceSize());
            });
    };

    return this;
}

function Sequence(sequenceId, sequenceSize){
    this.sequenceId = sequenceId;
    this.sequenceSize = sequenceSize;
    this.genes = [];

    this.getSequenceSize = function(){
        return this.sequenceSize;
    };

    return this;
}

function Backbone(){
    this.backbone = [[]];

    this.addHomologousRegion = function(seqId1,seqId2,start1,end1,start2,end2){
        if (this.backbone[seqId1] ===undefined){
            this.backbone[seqId1] = [];
        }

        if (this.backbone[seqId1][seqId2]===undefined){
            this.backbone[seqId1][seqId2] = [];
        }

        if (this.backbone[seqId2] ===undefined){
            this.backbone[seqId2] = [];
        }

        if (this.backbone[seqId2][seqId1]===undefined){
            this.backbone[seqId2][seqId1] = [];
        }

        this.backbone[seqId1][seqId2].push(new HomologousRegion(start1,end1,start2,end2));
        this.backbone[seqId2][seqId1].push(new HomologousRegion(start2,end2,start1,end1));
    };

    this.retrieveHomologousRegions = function(seqId1,seqId2){
        return this.backbone[seqId1][seqId2];
    }
}

function HomologousRegion(start1,end1,start2,end2){
    this.start1 = start1;
    this.end1 = end1;
    this.start2 = start2;
    this.end2 = end2;

    return this;
}



