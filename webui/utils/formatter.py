from django.conf import settings
from django.http import HttpResponse
import csv
import xlwt
from Bio.SeqFeature import SeqFeature, FeatureLocation
import pprint

# Not used
def formatResults(resultset, format, methods):
    if format in formats:
        formats[format](resultset, methods, filename)
    else:
        raise Exception("Unknown format")
    
def formatCSV(resultset, methods, filename, delimiter=False):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    
    if settings.DEBUG:
        pprint.pprint(resultset)
    
    if delimiter:
        writer = csv.writer(response, delimiter=delimiter)
    else:
        writer = csv.writer(response)
    
    line = ["Island start", "Island end", "Length", "Method", "Gene name", "Gene ID", "Locus", "Gene start", "Gene end", "Strand", "Product", "External Annotations"]
    writer.writerow(line)
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            if island.prediction_method.lower() not in allowedmethods:
                continue
            line = [island.island_start, island.island_end]
            line.append(int(island.island_end) - int(island.island_start))
            line += ["Predicted by at least one method", island.name, island.gene, island.locus, island.gene_start, island.gene_end, island.strand, island.product, makeAnnotationGroupingStr(island.virulence)]
            writer.writerow(line)

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:
            line = [island.island_start, island.island_end]
            line.append(int(island.island_end) - int(island.island_start))
            method = methodfullnames[island.prediction_method.lower()]
            line += [method, island.name, island.gene, island.locus, island.gene_start, island.gene_end, island.strand, island.product, island.virulence]
            writer.writerow(line)
            
    return response

def formatAnnotationCSV(annotations, filename, delimiter=False):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    
    if settings.DEBUG:
        pprint.pprint(annotations)
    
    if delimiter:
        writer = csv.writer(response, delimiter=delimiter)
    else:
        writer = csv.writer(response)
    
    line = ["Protein ID", "Type", "Source"]
    writer.writerow(line)
    
    # Loop through again for integrated
    for annotation in annotations:
        line = [annotation.name, annotation.source]
        line.append(makeAnnotationStr(annotation.external_id, annotation.source))
        writer.writerow(line)
            
    return response


def formatGenbank(resultset, seqobj, methods, filename):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    feature_offset = 0;
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            if island.prediction_method.lower() not in allowedmethods:
                continue
            seqobj.insertFeature(SeqFeature(FeatureLocation(island.start,island.end),
                                            type = "Misc", qualifiers={'note': 'Genomic Island: Predicted by at least one method'}), feature_offset)
            feature_offset += 1

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:
            seqobj.insertFeature(SeqFeature(FeatureLocation(island.start,island.end),
                                            type = "Misc", qualifiers={'note': 'Genomic Island: Predicted by ' + methodfullnames[island.prediction_method.lower()]}), feature_offset)
            feature_offset += 1

    for annotation in seqobj.fetchAnnotations():
        seqobj.insertFeature(SeqFeature(FeatureLocation(annotation[3], annotation[4]),
                                        type = "Misc", qualifiers={'note': 'Annotation: ' + annotation[2] + ', ' + annotation[0] + ': ' + makeAnnotationStr(annotation[1], annotation[0]) }), feature_offset)
        feature_offset += 1

    seqobj.writeGenbank(response)
    
    return response

def formatFasta(resultset, seqobj, methods, filename):
    response = HttpResponse(content_type='plain/text')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
   
    response.write(seqobj.generateFasta(seqtype = 'nuc', show_methods = True, methods = methods))
   
    return response

def formatTab(resultset, methods, filename):
    return formatCSV(resultset, methods, filename, '\t')

def formatAnnotationTab(annotations, filename):
    return formatAnnotationCSV(annotations, filename, '\t')

def formatExcel(resultset, methods, filename):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Islandviewer Results")

    row_num = 0
    
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    for col_num in xrange(len(excel_columns)):
        ws.write(row_num, col_num, excel_columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = excel_columns[col_num][1]
        
    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            if island.prediction_method.lower() not in allowedmethods:
                continue

            row_num += 1
            island_size = int(island.island_end) - int(island.island_start)
            row = [
                   island.island_start,
                   island.island_end,
                   island_size,
                   "Predicted by at least one method",
                   island.name,
                   island.gene,
                   island.locus,
                   island.gene_start,
                   island.gene_end,
                   island.strand,
                   island.product,
                   makeAnnotationGroupingStr(island.virulence)
                   ]
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:        
            row_num += 1
            island_size = int(island.island_end) - int(island.island_start)
            row = [
                   island.island_start,
                   island.island_end,
                   island_size,
                   methodfullnames[island.prediction_method.lower()],
                   island.name,
                   island.gene,
                   island.locus,
                   island.gene_start,
                   island.gene_end,
                   island.strand,
                   island.product,
                   island.virulence
                   ]
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
            
    wb.save(response)
    return response

def formatAnnotationExcel(annotations, filename):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Islandviewer Annotations")

    row_num = 0
    
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    for col_num in xrange(len(excel_annotation_columns)):
        ws.write(row_num, col_num, excel_annotation_columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = excel_annotation_columns[col_num][1]
        
    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    
    for annotation in annotations:
        row_num += 1
        row = [
            annotation.name,
            annotation.source
        ]
        row.append(makeAnnotationStr(annotation.external_id, annotation.source))
        for col_num in xrange(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

            
    wb.save(response)
    return response

def makeAnnotationStr(ext_id, source):

    if source == 'VFDB':
        return 'http://www.mgc.ac.cn/cgi-bin/VFs/vfs.cgi?VFID=' + ext_id
    elif source == 'PATRIC_VF':
        return 'http://patricbrc.org/portal/portal/patric/Feature?cType=feature&cId=' + ext_id
    elif source == 'Victors':
        return 'http://www.phidias.us/victors/gene_detail.php?c_mc_victor_id=' + ext_id
    elif source == 'CARD':
        return 'http://arpcard.mcmaster.ca/?q=CARD/ontology/' + ext_id
    elif source == 'RGI':
        return 'http://arpcard.mcmaster.ca/?q=CARD/ontology/' + ext_id
    elif source == 'PAG':
        return 'Pathogen-associated genes analysis (2014)'
    elif source == 'BLAST':
        return 'Annotation transfer from ' + ext_id
    else:
        return "Unknown"
    
def makeAnnotationGroupingStr(annotationstr):
    
    if not annotationstr:
        return ''
    
    annotations = annotationstr.split(',')
        
    virulence = []
    resistance = []
    pathogen = []
    for annotation in annotations:
        if annotation in ['VFDB', 'Victors', 'PATRIC_VF', 'BLAST']:
            virulence.append(annotation)
        elif annotation in ['RGI', 'CARD']:
            resistance.append(annotation)
        elif annotation in ['PAG']:
            pathogen.append(annotation)
            
    annotation_pieces = []
    
    if virulence:
        annotation_pieces.append('Virulence gene(' + ','.join(virulence) + ')')
    if resistance:
        annotation_pieces.append('Resistance gene(' + ','.join(resistance) + ')')
    if pathogen:
        annotation_pieces.append('Pathogen-associated gene(' + ','.join(pathogen) + ')')
        
    return ','.join(annotation_pieces)
    
excel_columns = [
    (u'Island start', 3000),
    (u'Island end', 3000),
    (u'Length', 2000),
    (u'Method', 8000),
    (u'Gene name', 6000),
    (u'Gene ID', 3000),
    (u'Locus', 4000),
    (u'Gene start', 3000),
    (u'Gene end', 3000),
    (u'Strand', 2000),
    (u'Product', 10000),
    (u'External Annotations', 10000)
                 
]    

excel_annotation_columns = [
    (u'Name', 4000),
    (u'Type', 3000),
    (u'Source', 15000)
]

allowedmethods = ['sigi', 'islandpick', 'dimob', 'islander']

downloadformats = {'genbank': formatGenbank,
                   'fasta': formatFasta,
                   'tab': formatTab,
                   'csv': formatCSV,
                   'excel': formatExcel
}

annotationformats = {'tab': formatAnnotationTab,
                     'csv': formatAnnotationCSV,
                     'excel': formatAnnotationExcel
}

downloadextensions = {'genbank': 'gbk',
                      'fasta': 'faa',
                      'tab': 'tsv',
                      'csv': 'csv',
                      'excel': 'xls'
}

methodfullnames = {'sigi': 'SIGI-HMM',
                   'dimob': 'IslandPath-DIMOB',
                   'islander': 'Islander',
                   'islandpick': 'IslandPick'
}
