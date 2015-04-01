FROM ubuntu:14.04
RUN apt-get update && apt-get -y install build-essential git python2.7 python2.7-dev wget time bedtools
RUN ln -s /usr/bin/python2.7 /usr/bin/python
# fix ubuntu's python package being totally broken
RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/
RUN git clone https://github.com/glennhickey/progressiveCactus.git
RUN cd progressiveCactus && git submodule update --init
RUN cd progressiveCactus && make
RUN git clone https://github.com/joelarmstrong/mafTools.git progressiveCactus/submodules/mafTools
RUN . progressiveCactus/environment && cd progressiveCactus/submodules/mafTools && make lib.all mafComparator.all
RUN git clone https://github.com/joelarmstrong/treeBuildingEvaluation progressiveCactus/submodules/treeBuildingEvaluation
#RUN cd progressiveCactus/submodules/treeBuildingEvaluation && export PROGRESSIVE_CACTUS_DIR=/progressiveCactus && make -e
COPY makeAndRunMammals.py /
CMD ["--help"]
ENTRYPOINT ["python", "makeAndRunMammals.py", "progressiveCactus"]
