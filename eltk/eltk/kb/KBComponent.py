# e-Linguistics Toolkit: KBComponent 
#
# Copyright (C) 2008 ELTK Project
# Author: Scott Farrar <farrar@u.washington.edu>
# URL: <http://purl.org/linguistics/eltk>
# For license information, see LICENSE.TXT
"""
The KBComponent module is  used to create some part of a knowledge base (i.e., a TBox or ABox). The KBComponent module provides a way to create a conceptualization of (some part of) the linguistics domain.  The module is used together with the Meta module (containing metaclasses) to bring an ontological conceptualization into the Python OOP framework. The implementation consists of a 2-layered model: the OWL+RDFS+RDF data model (a graph model) and Python's OOP model. 
"""
#note, fix rdflib imports when rdflib-2.5 is finalized

#rdflib-2.5
#from rdflib.graph import Graph
from rdflib.Graph import Graph


#from rdflib.term import URIRef
from rdflib.URIRef import URIRef

from rdflib import RDF
from rdflib.RDFS import RDFSNS
from rdflib import Literal


from eltk.namespace import GOLDNS, OWLNS

from eltk.kb import Meta

class KBComponent(object):

    """
    An instance of the  KBComponent class is a knowledge base (component) expressed in the Python OOP model. That is, it is a kind of 'context', because there could be multiple KB components and they need  not interact or refer to one another's contents. Using Description Logic terminology, a KBComponent could be either an ABox or TBox, or possibily a mixture, as allowed in the Semantic Web effort, by design.
    """
    def __init__(self,identifier=''):
        
        #identifier, should be URIRef ??
        self.identifier=identifier
        
        self.triples = {}
    
    def __getitem__(self,k):
        
        return self.triples[k]

        
    def __setitem__(self,subj,pred,obj):
        
        
        if subj not in self.triples.keys():
            self.triples[subj] = [(pred,obj,)]
        
        else:
            if (pred,obj,) not in self.triples[subj]: 
                self.triples[subj].append((pred,obj,))
            else:
                import logging
                logging.warn('The following triple is already in: '+self.identifier+'\n'+'('+subj.uri+' '+pred.uri+'...'+')' )
                
    #allows for a triple to be added to a kb like this:
    #   kb += (subj,pred,obj)
    def __iadd__(self,triple):
        
        self.__setitem__(triple[0],triple[1],triple[2])
        return self

    def getOWLClasses(self):
        """
        getOWLClasses returns only entities that are classes.
        
        :rtype: list
        """
        classes = []
        for attr in dir(self):
            entity = getattr(self,attr)
            if type(entity) is Meta.OWLClass:
                classes.append(entity)
        return classes

       
    #self.getOWLObjectProperties(self)
    #self.getOWLDatatypeProperties(self)
    #self.getABoxTriples(self)
 
    def buildRDFGraph(self,identifier=''):
        
        """
        buildRDFGraph creates an RDFLib graph object.
        
        :param identifier: the identifier string for the graph
        :type identifier: unicode
        :rtype: rdflib.Graph.Graph
        """
        
        #construct graph to be returned

        if identifier:
            #override original identifier
            graph = Graph(identifier=identifier)
        else:
            #otherwise keep identifier
            graph = Graph(identifier=self.identifier)


        #loop over triples in KBComponent
        for k in self.triples.keys():
            
            for v in self.triples[k]:
                object=''

                if type(v[1]) is str: 
                    object=Literal(v[1])
                
                #else: object = v[1].getURI()
                else: object = URIRef(v[1].uri)
                

                #graph.add((k.getURI(),URIRef(v[0].uri),object))
                graph.add((URIRef(k.uri),URIRef(v[0].uri),object))

        #always used these conventional labels
        graph.bind('rdfs', RDFSNS)    
        graph.bind('rdf', RDF.RDFNS,override=True)    
        graph.bind('owl',OWLNS)
        graph.bind('gold', GOLDNS)

        return graph




        

    def renderJSON(self,root):
        
        """
        renderJSON is a utility method to output a JSON rep of the KB. 
        
        :param root: The particular root class to from which to generate JSON
        :type root: OWLClass 
        :rtype: str
        """
        
        JSON_string = ''

        for cls in root.getSubClasses():
            
            JSON_string += cls + '\n'
            
        return JSON_string

if __name__=='__main__':
    
    """
    #for testing: deserialize a graph into a KB object, serialize it back out again
    from eltk.reader.LinkedDataReader import LinkedDataReader
    from eltk.config import ELTK_HOME
    
    ##########
    #read graph
    reader = LinkedDataReader()
    GOLD_graph = reader.parseGraph(ELTK_HOME+'/examples/inputfiles/gold-2008.owl')
    
    ############
    #de-serialize
    GOLD = reader.buildPyModel()


    ###########
    #serialize
    new_GOLD_graph= GOLD.buildRDFGraph('http://foo.org/gold')    

    new_GOLD_graph.serialize('gold-foo.owl')
    """

    """
    ######JSON########
    #outfile = open('concepts.json','w')
    #outfile.write(GOLD.renderJSON(GOLD.Abstract))
    """
    
    
    ##########add a simple triple#############
    
    mykb = KBComponent(URIRef('http://foo.org/myid'))
    
    Word = Meta.OWLClass.new(u'http://blah.org/Word')
    w = Word(u'w')
    hasConstituent = Meta.OWLObjectProperty.new(u'http://purl.org/linguistics/gold#hasConstituent')
    Morpheme = Meta.OWLClass.new(u'http://blah.org/Morpheme')
    m1 = Morpheme(u'http://blah.org/m1')
    m2 = Morpheme(u'http://purl.org/linguistics/gold#m2')
     

    mykb += (w,hasConstituent,m1)
    #mykb += (w,hasConstituent,m2)
    mykb += hasConstituent(w,m2)

    #returns a list of (pred,obj) pairs
    print mykb[w]
    
    #g = mykb.buildRDFGraph(URIRef('http://foo.org/blah'))
    g = mykb.buildRDFGraph()
    
    print g.identifier

    #[
    #    (<class 'eltk.kb.Meta.hasConstituent'>, <eltk.kb.Meta.Morpheme object at 0x7f97ddcb8450>), 
    #    (<class 'eltk.kb.Meta.hasConstituent'>, <eltk.kb.Meta.Morpheme object at 0x7f97ddcb8510>)
    #]
 
    #print mykb.w
    #<eltk.kb.Meta.Word object at 0x2a4c310>

    #print w.hasConstituent

    orthographicRep = Meta.OWLObjectProperty.new(u'http://purl.org/linguistics/gold#orthographicRep')
    mykb += (w,orthographicRep,'blah')

    mykb_graph = mykb.buildRDFGraph(u'http://purl.org/linguistics/foo')
    mykb_graph.serialize('foo.rdf')


