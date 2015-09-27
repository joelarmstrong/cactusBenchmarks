FROM ubuntu:14.04
RUN apt-get update && apt-get -y install build-essential git python2.7 python2.7-dev wget time bedtools r-base-core mafft fasttree
# fix ubuntu's python package being totally broken
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/
RUN git clone --recursive https://github.com/bd2kgenomics/cactus.git
RUN cd cactus && make
RUN git clone https://github.com/joelarmstrong/mafTools.git cactus/submodules/mafTools
RUN . cactus/environment && cd cactus/submodules/mafTools && make lib.all mafComparator.all
RUN git clone https://github.com/joelarmstrong/treeBuildingEvaluation cactus/submodules/treeBuildingEvaluation
RUN . cactus/environment && cd cactus/submodules/treeBuildingEvaluation && export PROGRESSIVE_CACTUS_DIR=/cactus && make -e
RUN . cactus/environment && pip install biopython
ADD . /cactusBenchmarks
ENV PYTHONPATH /cactusBenchmarks/src
CMD ["--help"]
ENTRYPOINT ["cactusBenchmarks/bin/runBenchmarks", "cactus", "cactusBenchmarks/testRegions"]
