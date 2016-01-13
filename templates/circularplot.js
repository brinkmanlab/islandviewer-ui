{% load virulencefactors %}
var {{ varName|default:"circular" }}data = [
{% comment %}Genes for linear view{% endcomment %}
	{ trackName: "{{ plotName|default:"circular" }}Genes",
	  trackType: "stranded",
	  inner_radius: 210,
	  outer_radius: 250,
	  visible: false,
	  showLabels: true,
	  showTooltip: true,
//skipLinear: true,
	  linear_skipInit: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: '{{ varName|default:'' }}islandviewerObj',{% endif %}
	  linear_mouseover: '{{ varName|default:'' }}islandviewerObj',
	  linear_mouseout: '{{ varName|default:'' }}islandviewerObj',
	  items: {{ genes|safe }}
	},
{% comment %}Contig Gap track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Contig_Gap",
	  trackType: "gap",
	  inner_radius: {{ contig_inner_radius|default:20 }},
	  outer_radius: {{ contig_outer_radius|default:245 }},
	  min_slice: true,
	  showTooltip: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',{% endif %}
	  items: {{ Contig_Gap|safe }}
	 },
{% comment %}Contig Alignment track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Alignment",
	  trackType: "track",
	  inner_radius: {{ alignment_inner_radius|default:245 }},
	  outer_radius: {{ alignment_outer_radius|default:250 }},
	  min_slice: true,
	  skipLinear: true,
	  showTooltip: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',{% endif %}
	  items: {{ Alignments|safe }}
	 },
{% comment %}Islandpick track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Islandpick",
	  trackType: "track",
	  inner_radius: {{ ip_inner_radius|default:50 }},
	  outer_radius: {{ ip_outer_radius|default:100 }},
	  min_slice: true,
	  mouseover_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseout_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseclick: '{{ varName|default:'' }}islandviewerObj',
	  linear_skipInit: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: '{{ varName|default:'' }}islandviewerObj',{% endif %}
	  linear_mouseover: '{{ varName|default:'' }}islandviewerObj',
	  linear_mouseout: '{{ varName|default:'' }}islandviewerObj',
	  items: {{ Islandpick|safe }}
	 },
{% comment %}SIGI track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Sigi",
	  trackType: "track",
	  inner_radius: {{ sigi_inner_radius|default:100 }},
	  outer_radius: {{ sigi_outer_radius|default:150 }},
	  mouseover_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseout_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseclick: '{{ varName|default:'' }}islandviewerObj',
	  linear_skipInit: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: '{{ varName|default:'' }}islandviewerObj',{% endif %}
	  linear_mouseover: '{{ varName|default:'' }}islandviewerObj',
	  linear_mouseout: '{{ varName|default:'' }}islandviewerObj',
	  items: {{ Sigi|safe }}
	 },
{% comment %}Dimob track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Dimob",
	  trackType: "track",
	  inner_radius: {{ dimob_inner_radius|default:150 }},
	  outer_radius: {{ dimob_outer_radius|default:200 }},
	  min_slice: true,
	  mouseover_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseout_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseclick: '{{ varName|default:'' }}islandviewerObj',
	  linear_skipInit: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: '{{ varName|default:'' }}islandviewerObj',{% endif %}
	  linear_mouseover: '{{ varName|default:'' }}islandviewerObj',
	  linear_mouseout: '{{ varName|default:'' }}islandviewerObj',
	  items: {{ Dimob|safe }}
	 },
{% comment %}Integrated track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Integrated",
	  trackType: "track",
	  inner_radius: {{ int_inner_radius|default:215 }},
	  outer_radius: {{ int_outer_radius|default:245 }},
	  mouseover_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseout_callback: '{{ varName|default:'' }}islandviewerObj',
	  mouseclick: '{{ varName|default:'' }}islandviewerObj',
	  skipLinear: true,
	  items: {{ Integrated|safe }}
	 },
{% comment %}GC Plot track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}GCPlot",
	  trackType: "plot",
	  plot_radius: {{ gc_plot_radius|default:150 }},
	  plot_width: {{ gc_plot_width|default:75 }},
	  bp_per_element: {{ gc_bp_per_element|default:10000 }},
	  plot_min: {{ gc.min|default:0 }},
	  plot_max: {{ gc.max|default:0 }},
	  plot_mean: {{ gc.mean|default:0 }},
	  items: [
	          {{ gc.gc }}
	         ]
	 },
{% comment %}Virulence factor data{% endcomment %}
	{% if vir_factors %}
	{ trackName: "{{ plotName|default:"circular" }}Virulence",
	  trackType: 'glyph',
	  glyphType: '{{ virulenceShape|default:"circle" }}',
	  radius: {{ virulenceRadius|default:175 }},
	  pixel_spacing: 3,
          linear_pixel_spacing: 6,
	  glyph_buffer: 3,
	  linear_glyph_buffer: 6,
	  glyphSize: 20,
	  linear_glyphSize: 30,
          linear_padding: 4,
          linear_height: 5,
          linear_invert: true,
	  showTooltip: true,
	  linear_mouseover: '{{ varName|default:'' }}islandviewerObj',
	  linear_mouseout: '{{ varName|default:'' }}islandviewerObj',
          linear_mouseclick: '{{ varName|default:'' }}islandviewerObj',
	  showTooltip: true,
	  items: {{ vir_factors|safe }}
	}{% endif %}
];

var {{ varName|default:"circular" }}_genomesize = {{ genomesize }};
var {{ varName|default:"circular" }}_extid = "{{ ext_id }}";
var {{ varName|default:"circular" }}_genomename = "{{ genomename }}";
var {{ varName|default:"circular" }}_aid = "{{ aid }}";

{% comment %}Skip the entire code section if we're just pulling in another plot's data{% endcomment %}
{% if not skip_initialize %}

var islandviewerObj = new Islandviewer('{{ aid }}', '{{ext_id}}', {{ genomesize|default:"0" }}, "{{ genomename }}", {{ plotName|default:"circular" }}data);
// {{ genomename|pprint }}
update_legend();

var {{ plotName|default:"circular" }}layout = {genomesize: {{ genomesize }}, container: "{{ container }}", h: 500, w: 500, ExtraWidthX: 55, TranslateX: 25, ExtraWidthY: 40, TranslateY: 20, movecursor: true, dblclick: '{{ varName|default:'' }}islandviewerObj' };

var {{ varName|default:"circular" }}containerid =  "{{ container }}".slice(1);
$('{{ container }}').draggable({ handle: ".move_" +  {{ varName|default:"circular" }}containerid });
//var {{ plotName|default:"circular" }}Track = new circularTrack({{ plotName|default:"circular" }}layout, {{ plotName|default:"circular" }}data);
var {{ plotName|default:"circular" }}TrackObj = islandviewerObj.addCircularPlot({{ plotName|default:"circular" }}layout);

$('#loadingimg').remove();

var {{ plotName|default:"circular" }}Linearlayout = {genomesize: {{ genomesize }}, container: "{{ container }}linear", width: 600, height: 135, bottom_margin:0, initStart:0, initEnd: Math.min(1000, {{ genomesize }})};
//var {{ plotName|default:"circular" }}LinearTrack = new genomeTrack({{ plotName|default:"circular" }}Linearlayout, {{ plotName|default:"circular" }}data);
var {{ plotName|default:"circular" }}LinearTrack = islandviewerObj.addLinearPlot({{ plotName|default:"circular" }}Linearlayout);

{{ plotName|default:"circular" }}TrackObj.attachBrush({{ plotName|default:"circular" }}LinearTrack);
{{ plotName|default:"circular" }}LinearTrack.addBrushCallback({{ plotName|default:"circular" }}TrackObj);

{{ plotName|default:"circular" }}TrackObj.attachBrush(islandviewerObj);
{{ plotName|default:"circular" }}LinearTrack.addBrushCallback(islandviewerObj);

$('#gene_dialog').dialog( { position: { my: "left top", at: "right top", of: "{{ container }}" },
	                    height: 550, width: 450,
			    title: "Genes",
	                    autoOpen: false,
          	            close: function() {
	    $('.circularcontainer').removeClass('outline_plot');
	}
	    } );

//$('#genome_selector_dialog').dialog( { position: { my: "center", at: "center", of: window },
//                                       height: 300, width: 600,
//                                       title: "Select a genome",
//                                       autoOpen: true
//                                      } );

function updateStrand(cb, strand) {
  var track = '';

  switch(strand) {
  case "islandpick":
    track = "{{ plotName|default:"circular" }}Islandpick";
    break;
  case "sigi":
    track = "{{ plotName|default:"circular" }}Sigi";
    break;
  case "dimob":
    track = "{{ plotName|default:"circular" }}Dimob";
    break;
  case "integrated":
    track = "{{ plotName|default:"circular" }}Integrated";
    break;
  case "contig":
    track = "{{ plotName|default:"circular" }}Contig_Gap";
    break;
  case "alignment":
    track = "{{ plotName|default:"circular" }}Alignment";
    break;
  }

  if(cb.checked) {
    {{ plotName|default:"circular" }}TrackObj.showTrack(track);
    if('undefined' !== typeof window.secondTrackObj) {
      window.secondTrackObj.showTrack(track);
    }
  } else {
    {{ plotName|default:"circular" }}TrackObj.hideTrack(track);
    if('undefined' !== typeof window.secondTrackObj) {
      window.secondTrackObj.hideTrack(track);
    }
  }
}

//var virulenceMappings = { 'VFDB': ['VFDB', 'Victors', 'Patric_VF'],
var virulenceMappings = { 'VFDB': ['VFDB'],
			  'ARDB': ['ARDB', 'CARD'],
			  'BLAST': ['BLAST'],
			  'RGI': ['RGI'],
			  'PAG': ['PAG']
			};

function updateVirulence(cb, vir) {

    var vir_factor = vir;
    //  var vir_factors =  virulenceMappings[vir];
    //  for(var x = 0; x < vir_factors.length; x++) {
    //      vir_factor = vir_factors[x];
//      console.log(vir_factor);

      if(cb.checked) {
	  //	  console.log("showing: " + vir_factor);
	  {{ plotName|default:"circular" }}TrackObj.showGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
	  if('undefined' !== typeof window.secondTrackObj) {
	      window.secondTrackObj.showGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
	  }
      } else {
	  {{ plotName|default:"circular" }}TrackObj.hideGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
	  if('undefined' !== typeof window.secondTrackObj) {
	      window.secondTrackObj.hideGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
	  }
      }
      //  }
}

function updateTracks(ivObj) {
       $('input:checkbox.islandmethod:not(:checked)').each(function () {
	    var track = $(this).attr('id').replace(/^show/,'');
	    if($(this).prop('disabled')) {
		return;
	    }

	    ivObj.maskTrackType(track);
	});

       $('input:checkbox.virulencemethod:not(:checked)').each(function () {
	    var vir_factor = $(this).attr('id').replace(/^show/,'');
	    if($(this).prop('disabled')) {
		return;
	    }

	    ivObj.maskGlyphType(vir_factor);
	});
 
}

window.onload = function() {

  {{ plotName|default:"circular" }}TrackObj.hideBrush();

  for(var i=0; i < {{ plotName|default:"circular" }}data.length; i++) {
    if({{ plotName|default:"circular" }}data[i].trackName == "{{ plotName|default:"circular" }}Integrated") {
      if({{ plotName|default:"circular" }}data[i].items.length > 0) {
        item = {{ plotName|default:"circular" }}data[i].items[0];
	var wrapperdiv = $('#circularchartlinearwrapper');
        if(wrapperdiv.hasClass("hidden")) {
        wrapperdiv.removeClass("hidden").addClass("visible");
      }

      var half_range = (item.end - item.start)/2;
      {{ plotName|default:"circular" }}LinearTrack.update(Math.max(0,(item.start-half_range)), Math.min({{ genomesize }}, (item.end+half_range)));
//      {{ plotName|default:"circular" }}LinearTrack.update(2840000,2905000);

      {{ plotName|default:"circular" }}TrackObj.moveBrushbyBP(Math.max(0,(item.start-half_range)), 
                                                       Math.min({{ genomesize }}, (item.end+half_range)));

      {{ plotName|default:"circular" }}TrackObj.showBrush();

      islandviewerObj.update_finished(Math.max(0,(item.start-half_range)), Math.min({{ genomesize }}, (item.end+half_range)));
      }
    }
  }

  $("#second_genome_select").chosen({width: "525px"});

  initialize_gene_search();

  if('undefined' !== typeof reloadStr) {
      //      console.log(reloadStr);
      reload(reloadStr);
  }
  //  reload();
//  load_second();

  {% if contig_controls %}
  $('#contigcontrols').show();
  {% endif %}

};

function show_gene_search() {

    if($('#gene_search_dialog').is(":visible")) {
	hide_gene_search();
	return;
    }

    $('#show_gene_search').html("Hide Search");
    $('#gene_search_dialog').slideToggle('fast');
    $("#gene_search_input").focus();

}

function hide_gene_search() {
    $('#show_gene_search').html("Search Genes");
    $("#gene_search_input").val('');
    $('#gene_search_dialog').slideToggle('fast');

}

$('#close_gene_search').on('click', function() {
    hide_gene_search();
});

$('#close_select_genome').on('click', function() {
    close_genome_dialog();
});

$('#close_url').on('click', function() {
    close_url_dialog();
});

function close_url_dialog() {
    if($('#url_dialog').is(":visible")) {
	$('#url_dialog').slideToggle('fast');
    }
}

$('#url_input').on('click', function() {
    $(this).select();
});

function initialize_gene_search() {

    $("#gene_search_input").autocomplete({
	source: function(request, response) {
	    params = { term: request.term };
	    if('undefined' !== typeof window.secondislandviewerObj) {
		params['second_ext_id'] = window.secondislandviewerObj.ext_id;
	    }
	    $.getJSON('{% url 'searchgenes' ext_id %}', params, 
		      response);
	},
	minLength: 3,
	select: function( event, ui ) {
	    $('.circularcontainer').removeClass('highlight_plot');
	    item = ui.item;
	    var range = (item.end - item.start) * 10;
	    // Forcus to a window 10x the gene size
	    if(item.extid == '{{ ext_id }}') {
		islandviewerObj.focus((item.start - range), (item.end + range), { highlight_sel: '#gene_overlay_' + item.id });
	    } else if(('undefined' !== typeof window.secondislandviewerObj) && item.extid == window.secondislandviewerObj.ext_id) {
		window.secondislandviewerObj.focus((item.start - range), (item.end + range), { highlight_sel: '#gene_overlay_' + item.id });
	    }
	    $(this).val(item.name + ', ' + item.product + ' (' + item.gene + ') ' + '[' + item.start + '..' + item.end + ']');
	    $(this).blur();
	    return false;
	},
	focus: function( event, ui ) {
	    if('undefined' == typeof window.secondislandviewerObj) {
		return true;
	    }
	    $('.circularcontainer').removeClass('highlight_plot');
	    item = ui.item;
	    $('.plot_' + item.extid.replace('.','')).addClass('highlight_plot');
	    return true;
	},
	close: function( event, ui ) {
	    $('.circularcontainer').removeClass('highlight_plot');
	},
    }).focus(function() {
	    $(this).val('');
    }).autocomplete( "instance" )._renderItem = function( ul, item ) {
	return $( "<li class=\"searchItem\">" )
	    .append(item.name + ', ' + item.product + ' (' + item.gene + ') ' + '[' + item.start + '..' + item.end + ']')
	    .appendTo( ul );
	};
    
}

function addSearchHighlight(elem) {
    $(elem).addClass("highlight_row");
}

function serialize() {

    var params = {};
    params['m'] = islandviewerObj.serialize();

    var unchecked = [];
    $('input:checkbox.islandmethod:not(:checked)').each(function () {
	    unchecked.push(this.id);
	});
    $('input:checkbox.virulencemethod:not(:checked)').each(function () {
	    unchecked.push(this.id);
	});
    params['un'] = unchecked;

    if('undefined' !== typeof window.secondislandviewerObj) {
	params['s'] = window.secondislandviewerObj.serialize();
	//	params['s']['id'] = window.secondislandviewerObj.aid;
    }

    if($('#gene_dialog').dialog( "isOpen" ) === false) {
	params['d'] = {v: false};
    } else {
	params['d'] = {v: true};

	var o = $('#gene_dialog').dialog( "open" ).offset();
	//	params['d']['p'] = $('#gene_dialog').dialog('option', 'position');
	params['d']['t'] = o.top;
	params['d']['l'] = o.left;

    }

    console.log(params);

    uri = encodeURIComponent(JSON.stringify(params));

    //    decoded = decodeURIComponent(uri);

    //    console.log(decoded);

    url = insertParam('load', uri);

    console.log(url);

    if($('#url_dialog').is(":hidden")) {
	$('#url_dialog').slideToggle('fast');
    }

    $('#url_input').val(url);
    $('#url_input').select();
}
 
function insertParam(key, value)
{
    key = encodeURI(key); value = encodeURI(value);

    var kvp = document.location.search.substr(1).split('&');

    var i=kvp.length; var x; while(i--) 
    {
        x = kvp[i].split('=');

        if (x[0]==key)
        {
            x[1] = value;
            kvp[i] = x.join('=');
            break;
        }
    }

    if(i<0) {kvp[kvp.length] = [key,value].join('=');}

    //this will reload the page, it's likely better to store this until finished
    //    document.location.search = kvp.join('&'); 
    return document.location.href + '?' + kvp.join('&'); 
}

function reload(paramsStr) {
    features = {s: 912360, e: 1032732, c: 600, x: 'auto', y: 'auto', l: 800};

    try {
	params = $.parseJSON(decodeURIComponent(paramsStr));
    } catch(err) {
	alert("Error decoding url.");
    }
    //    console.log(params);

    if('undefined' !== typeof params['m']) {
	islandviewerObj.reload(params['m']);
    }

    if('undefined' !== typeof params['un']) {
	for(var i = 0; i < params['un'].length; i++) {
	    var method = params['un'][i];
	    $('#' + method).click();
	}
    }

    if('undefined' !== typeof params['d']) {
    	if(params['d']['v'] == true) {
	    if('undefined' !== typeof params['d']['t'] && 'undefined' !== typeof params['d']['l']) {
		$('#gene_dialog').dialog( 'widget' ).offset({ top: params['d']['t'], left: params['d']['l'] });
	    }
	} else {
	    $('#gene_dialog').dialog( 'close' );
	    if('undefined' !== typeof params['s']) {
		params['s']['d'] = false;
	    }
	}
    }

    if('undefined' !== typeof params['s'] && 'undefined' !== typeof params['s']['id']) {
	obj = load_second(params['s']['id'], params['s']);
	//	obj.reload(params['s']);
    }

}

function close_genome_dialog() {

    $('#show_second_link').html("Visualize two genomes");
    $('#genome_selector_dialog').slideToggle('fast');

}

function show_genome_dialog() {
  url = '{% url 'browsejson'  %}';

  if($('#genome_selector_dialog').is(":visible")) {
      close_genome_dialog();
      return;
  }

  $.ajax({
	    url: url,
	    type: "get",
            dataType: "json",
	        beforeSend: function () { 
	    		$("#loadingspinner").show("fast");
	    	},
	    success: function(data) {
      		  $("#loadingspinner").hide("fast");
              $("#second_genome_select").empty();
              var genomes = data.genomes;
              for(var i = 0; i < genomes.length; ++i) {
                $("#second_genome_select").append("<option value=\"" + genomes[i].aid + "\">" + genomes[i].name + " (" + genomes[i].ext_id + ")</option>\n");
              }

              $('#show_second_link').html("Hide dialog");
              $('#genome_selector_dialog').slideToggle('fast');
              $("#second_genome_select").trigger("chosen:updated");
//              $('#genome_selector_dialog').dialog("open");

          }, 
          error: function (xhr, ajaxOptions, thrownError) {
	    	$("#loadingspinner").hide("fast");
            console.log(xhr.status);
            console.log(thrownError);
          }


  });
}

function load_second(aidParam, reloadParams) {
  aid = $("#second_genome_select").val();

  if('undefined' !== typeof aidParam) {
      aid = aidParam;
  }

//  console.log("loading " + aid);

  if($('#genome_selector_dialog').is(":visible")) {
      $('#genome_selector_dialog').slideToggle();
  }

  $('#show_second_link').html("Visualize two genomes");
  var title = $("#second_genome_select").find(":selected").text();

  $('#second_genome_title_wrapper').show();

  var url = "{% url 'circularplotjs' '9999' %}".replace("9999", aid);
  url += "?skipinit=true&varname=second";
//  var url = "/islandviewer/plot/553?skipinit=true&varname=second";

//  console.log(url);

  $("#loadingspinner").show("fast");

  $.getScript( url, function() {
//    console.log("loaded");
//    console.log(second_genomesize);

    window.secondislandviewerObj = new Islandviewer(aid, second_extid, second_genomesize, second_genomename, seconddata);
    $('#second_genome_title').html(second_genomename);

    // We can update hte legend here because it only depends on the dataset
    update_legend();

    // Update the tracks if any are turned off
    updateTracks(window.secondislandviewerObj);

    var secondlayout = {genomesize: second_genomesize, container: "#rightplot", h: 500, w: 500, ExtraWidthX: 55, TranslateX: 25, ExtraWidthY: 40, TranslateY: 20, movecursor: true, plotid: 'circularchart', dblclick: 'secondislandviewerObj' };
//    var secondTrackObj = new circularTrack(secondlayout, seconddata);
    window.secondTrackObj = secondislandviewerObj.addCircularPlot(secondlayout);    
    $('#rightplot').draggable({ handle: ".move_rightplot" });

    var secondLinearlayout = {genomesize: second_genomesize, container: "#secondchartlinear", width: 600, height: 135, bottom_margin:0, plotid: 'circularchartlinear'};
//    var secondLinearTrack = new genomeTrack(secondLinearlayout, seconddata);
    window.secondLinearTrack = secondislandviewerObj.addLinearPlot(secondLinearlayout);

    secondTrackObj.attachBrush(secondLinearTrack);
    secondLinearTrack.addBrushCallback(secondTrackObj);

    secondTrackObj.attachBrush(secondislandviewerObj);
    secondLinearTrack.addBrushCallback(secondislandviewerObj);

    // Move the brush to the first island
    for(var i=0; i < seconddata.length; i++) {
      if(seconddata[i].trackName == "{{ plotName|default:"circular" }}Integrated") {
        if(seconddata[i].items.length > 0) {
          item = seconddata[i].items[0];
        }

        var half_range = (item.end - item.start)/2;
        secondLinearTrack.update(Math.max(0,(item.start-half_range)), Math.min(second_genomesize, (item.end+half_range)));
//      {{ plotName|default:"circular" }}LinearTrack.update(2840000,2905000);

        secondTrackObj.moveBrushbyBP(Math.max(0,(item.start-half_range)), 
                                                       Math.min(second_genomesize, (item.end+half_range)));

        secondTrackObj.showBrush();

        secondislandviewerObj.update_finished(Math.max(0,(item.start-half_range)), Math.min(second_genomesize, (item.end+half_range)));
      }
    }

    // Next we need to display the gi table, this will involve
    // changing the div from hidden to inline-block,
    // resizing the existing gitable to fit, and calling the redraw
    // function for the table headers
    $('#main_gitable').switchClass('gitable_fullwidth', 'gitable_halfwidth', 400, 'swing', function() { oTable.fnAdjustColumnSizing(); });
    $('#right_gitable').switchClass('hidden', 'visinline', 400, 'swing', function() { 
      var url = "{% url 'tablejson' aid='9999' %}".replace('9999', aid);
      if('undefined' !== typeof secondoTable) {

        secondoTable.fnSettings().sAjaxSource= "url";
        secondoTable.fnReloadAjax(url);
//        secondoTable.fnDraw();
      } else {

        window.secondoTable = create_gitable("rightgitable", url, 'window.secondislandviewerObj'); 
      }

      $('#linearname').html({{ varName|default:"circular" }}_genomename);
      $('#secondlinearname').html(second_genomename);
    });
    


      }).done(function() {
	      if('undefined' !== typeof reloadParams) {
		  window.secondislandviewerObj.reload(reloadParams);
	      }

	      $("#loadingspinner").hide("fast");

      }); // end getScript()

  return window.secondislandviewerObj;
}

function hide_second() {
  $('#second_genome_title_wrapper').hide();

  $('#rightplot').html('');
  $('#secondchartlinear').html('');

  $('.circularcontainer').removeClass('outline_plot');

  window.secondislandviewerObj = undefined;
  secondTrackObj = undefined;
  secondLinearTrack = undefined;

  update_legend();

  $('#linearname').html('');
  $('#secondlinearname').html('');

  $('#right_gitable').switchClass('visinline', 'hidden', function() {

      $('#main_gitable').switchClass('gitable_halfwidth', 'gitable_fullwidth', 400, 'swing', function() { oTable.fnAdjustColumnSizing(); });
  });
}

function show_islandpick_genomes() {
	islandviewerObj.showIslandpickGenomes({{ varName|default:"circular" }}_aid);
}

function update_legend() {
  var methods = islandviewerObj.findMethods();

  // Merge in the second genome's methods
  if('undefined' !== typeof secondislandviewerObj) {
    secondmethods = secondislandviewerObj.findMethods();

    // Go this way around to force a deep copy of the object
    for(var key in methods) {
      if(methods.hasOwnProperty(key)) {
        secondmethods[key] = true;
      }
    }

    methods = secondmethods;
  }

//console.log(methods);
  // Now update the legend
  var allmethods = ['circularIntegrated', 'circularIslandpick', 'circularSigi', 'circularDimob', 'PAG', 'VFDB', 'ARDB', 'CARD', 'RGI', 'Victors', 'PATRIC_VF', 'BLAST'];
  // First disable all checkboxes and say nothing is run
  $('.methodcheckbox').each( function() {
      $(this).attr("disabled", true);
  });
  for(var i = 0; i < allmethods.length; i++ ) {
    method = allmethods[i];
    if(methods[method]) {
      $('.show' + method).each( function() {
	  $(this).removeAttr("disabled");
      });
      $('.no' + method).hide();
//      $('#show' + method).removeAttr("disabled");
//      $('#no' + method).hide();
//    } else {
//      $('#show' + method).attr("disabled", true);
//      $('#no' + method).show();
//      // We'll do the opposite with classes of this name to hide elements
//      // for non-esxistant analysis types, if needed
//      $('.no' + method).hide();
    }
  }

}

function feature_tour() {

	var intro = introJs();
	var dialog_was_open = false;
//        $('#download_dialog').removeClass("hidden");
	show_download();
        if($('#gene_dialog').dialog( "isOpen" ) === false) {
          $('#gene_dialog').dialog("open");
          dialog_was_open = false;
        } else {
          dialog_was_open = true;
        }
        intro.onexit(function() {
          if(dialog_was_open === false) {
	    $('#gene_dialog').dialog( "close" );
          }
	  hide_download();
//          $('#download_dialog').addClass("hidden");
        });

        intro.oncomplete(function() {
          if(dialog_was_open === false) {
	    $('#gene_dialog').dialog( "close" );
          }
	  hide_download();
//          $('#download_dialog').addClass("hidden");
        });

	intro.setOptions({
	  showStepNumbers: false,
	  steps: [
	    {
	      element: document.querySelector('{{ container }}'),
	      intro: "<b>Circular viewer</b><br />In the circular viewer you can click on islands to zoom the horizontal viewer below to a location and pop up a context list of genes and islands.<br />&nbsp;<br />The black circular markers can be dragged to refocus and zoom the linear viewer.<br />&nbsp;<br />Double clicking on the plot will recentre the region being viewed under the mouse pointer.<br />&nbsp;<br />The plot can be resized using the drag bar in the lower right corner.",
	      position: 'right'
	    },
	    {
	      element: '{{ container }}linear',
	      intro: "<b>Horizontal viewer</b><br />In the horizontal viewer you can zoom and scroll using your mouse and mousewheel respectively (or use two fingers on your touch pad depending on your device).<br />&nbsp;<br />Hovering over elements will highlight the corresponding gene(s) in the vertical viewer.<br />&nbsp;<br />Clicking on a gene will take you to the NCBI gene card, clicking on an island will take you the corresponding island entry in the table below, and clicking on a VF/AMR annotation will take you to the external reference for this annotation.<br />&nbsp;<br />The plot can be resized using the drag bar on the right side.",
	      position: 'top'
	    },
	    {
	      element: '#gene_dialog',
	      intro: "<b>Vertical viewer</b><br />The gene dialog will show all the genes in the range currently visible in the horizontal viewer, and bounded by the shaded region bounded by the black circles in the circular viewer. Islands, virulence factors, etc are marked with colour coded glyphs.<br />&nbsp;<br />The dialog may be resized and moved using your mouse.",
	      position: 'left'
	    },
	    {
	      element: document.querySelector('#legend'),
	      intro: "<b>Legend</b><br />Individual tracks can be turned on and off using legend. They will be dynamically added/removed from the circular viewer.",
	      position: 'right'
	    },
	    {
	      element: document.querySelector('#show_second_link'),
	      intro: "<b>Visualize two genomes</b><br />A second genome can be displayed to allow comparison of results (highly similar genomes are most suitable). Click here to show the genome selector.",
	      position: 'right'
	    },
	    {
	      element: document.querySelector('#download_container'),
	      intro: "<b>Download dialog</b><br />Results and the circular viewer can be downloaded via the download dialog, click to expand it.",
	      position: 'top'
	    },
	    {
	      element: document.querySelector('#gitableheader'),
	      intro: "<b>Genomic Islands table</b><br />Below is a summary of results grouped by detection method.",
	      position: 'top'
	    },
	    {
	      element: document.querySelector('#save_view'),
	      intro: "<b>Save view</b><br />A link can be created to save your current view (zoom level and focus) in order to come back later or share.",
	      position: 'top'
	    },
	    {
	      element: document.querySelector('#legend_help'),
	      intro: "<b>More questions?</b><br />For more information see our help page and our FAQ, if you still have questions don't hesitate to contact us.",
	      position: 'top'
	    }
	  ]
	});

	intro.start();
}

{% endif %}
