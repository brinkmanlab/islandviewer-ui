base_fixtures = ['base_fixtures.json']
namecache_fixtures = ['namecache.json']
analysis_fixtures = base_fixtures + namecache_fixtures + ['islands_and_genes.json']
islandviewer_fixtures = base_fixtures + namecache_fixtures + ['islands_and_genes.json', 'distance.json', 'virulence.json']
microbedb_fixtures = ['microbedb_version.json', 'taxonomy.json', 'genomeproject.json', 'replicon.json']
all_test_fixtures = islandviewer_fixtures + microbedb_fixtures
