from rdflib import BNode, Graph, Literal, Namespace, URIRef
import json


GEO = Namespace("http://www.opengis.net/ont/geosparql#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
EX = Namespace("http://twin-example/zurich#")
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
XSD = Namespace('http://www.w3.org/2001/XMLSchema#')
IRRIG = Namespace('http://www.w3id.org/def/irrig#')

def addGeometry(subject,feature,id,g):
    # point
    geometry = feature['geometry']
    predicate = URIRef(GEO.hasGeometry)
    pointObj = URIRef(f'{EX}{geometry["type"]}_{id}')
    g.add((subject,predicate,pointObj))
    # geo:asWKT "<http://www.opengis.net/def/crs/OGC/1.3/CRS84> Point(46.22774431495321 6.132807148725261)"^^geo:wktLiteral
    g.add((pointObj, GEO.asWKT, Literal(f'<http://www.opengis.net/def/crs/OGC/1.3/CRS84> Point({geometry["coordinates"][0]} {geometry["coordinates"][1]})',datatype=URIRef(GEO.wktLiteral))))
    # <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> geo:Point
    g.add((pointObj,RDF.type,GEO.Point))

def addFamilyInformation(subject,feature,id,g):
    properties = feature['properties']
    # retrieve information
    genus = properties['baumgattunglat']
    species = properties['baumartlat']
    name = properties['baumnamelat']
    nameDE = properties['baumnamedeu']
    treetopdiameter = properties['kronendurchmesser']
    street = properties['strasse']
    neighbourhood = properties['quartier']
    category = properties['kategorie']
    poiId = properties['poi_id']
    # add triples
    g.add((subject,SKOS.prefLabel,Literal(name,'en')))
    g.add((subject, SKOS.altLabel,Literal(nameDE,'de')))
    g.add((subject,SKOS.altLabel,Literal(species,'en')))
    # broader concept
    bn = BNode()
    g.add((subject,SKOS.broader,bn))
    g.add((bn,SKOS.prefLabel,Literal(genus,'en')))
    # other data
    g.add((subject,EX.hasDiameter,Literal(treetopdiameter,datatype=URIRef(XSD.integer))))
    g.add((subject,EX.street,Literal(street,datatype=URIRef(XSD.string))))
    g.add((subject,EX.neighbourhood,Literal(neighbourhood,datatype=URIRef(XSD.string))))
    g.add((subject,EX.category,Literal(category,datatype=URIRef(XSD.string))))
    g.add((subject,EX.poiId,Literal(poiId,datatype=URIRef(XSD.string))))

def bindPrefixes(g):
    g.bind("geo",GEO)
    g.bind("rdf",RDF)
    g.bind("ex",EX)
    g.bind('skos',SKOS)
    g.bind('xsd',XSD)
    g.bind('irrig',IRRIG)


def main():
    # Create a Graph
    g = Graph()
    bindPrefixes(g)
    with open("./dataset/data/baumkataster_baumstandorte.json", "r") as read_file:
        data = json.load(read_file)
        
        # features 
        features = data['features']

        for feature in features:
            objId = feature["properties"]["objid"]
            subject = URIRef(f'{EX}tree_{objId}')
            g.add((subject,RDF.type,IRRIG.Tree))
            addGeometry(subject,feature,objId,g)
            addFamilyInformation(subject,feature,objId,g)
        outpath = f'./baumkataster.ttl'
        g.serialize(format="turtle",destination=outpath)

if __name__ == "__main__":
    main()
