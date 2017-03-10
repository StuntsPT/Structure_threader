#!/usr/bin/python3

# Copyright 2015 Francisco Pina Martins <f.pinamartins@gmail.com>
# This file is part of structure_threader.
# structure_threader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# structure_threader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with structure_threader. If not, see <http://www.gnu.org/licenses/>.

import plotly.plotly as py
from plotly.offline import plot
import plotly.graph_objs as go
from plotly import tools
import colorlover as cl

from os.path import basename, join, splitext
from collections import Counter, defaultdict, OrderedDict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
    from plotter.html_template import ploty_html
except ImportError:
    from structure_threader.plotter.html_template import ploty_html

# Create color pallete
c = cl.scales["12"]["qual"]["Set3"]


class PlotK:
    """
    Individual class object meant to parse and store information of the meanQ
    values for single K value output files as a numpy array.
    THIS DOES NOT INCLUDE INFORMATION OF THE POPFILE. That information will
    be transverse to all output files and stored in the PlotList object.
    """

    def __init__(self, kfile, fmt, get_indv=False):
        """
        Automatically parses the kfile (meanQ file) according to the fmt
        (format). Also sets all instance attributes

        :param kfile (str): Path to k output file.
        :param fmt (str) ["structure", "faststructure", "maverick"]:
         The format of the k output file.
        """

        """
        Sets the path of the output K file
        """
        self.file_path = kfile

        """
        Stores the format of the output K file
        """
        self.fmt = fmt

        """
        Stores the number of K clusters
        """
        self.k = None

        """
        Stores the number of individual taxa
        """
        self.nind = None

        """
        Stores the meanQ array. This is a numpy structured array of
        float64 dtype.
        """
        self.qvals = None

        """
        Establishes whether the individual sample names should
        get parsed
        """
        self.get_indv = get_indv

        """
        Array that continas the list of individualnames. This will
        only be populated when get_indv argument is set to True
        """
        self.indv = []

        parse_methods = {"structure": self._parse_structure,
                         "fastStructure": self._parse_faststructure,
                         "maverick": self._parse_maverick}

        # Let the parsing begin
        parse_methods[self.fmt]()

        # Set K value
        self.k = self.qvals.shape[1]

    def _parse_usepopinfo(self, fhandle, end_string):
        """
        This method handles the parsing of a Structure output file when the
        USEPOPINFO flag is specified.

        An example of the Structure output with a USEPOPINFO flag:

        Inferred ancestry of individuals:
        Probability of being from assumed population | prob of other pops
                Label (%Miss) Pop
          1 neoNAAri1    (0)    1 :  0.999 | Pop 2: 0.000 0.000 0.001  |
          2 neoNAAri2    (0)    1 :  1.000 | Pop 2: 0.000 0.000 0.000  |
          3 neoNAAri3    (0)    1 :  1.000 | Pop 2: 0.000 0.000 0.000  |
          4 neoNAAri4    (0)    1 :  1.000 | Pop 2: 0.000 0.000 0.000  |

        In this case K = 2 and there are 2 populations. The value before the
        first "|" represents the probability assignment for the best cluster.
        Then, for each array of values after a "|" the probability assignment
        to all other populations is provided.

        :param fhandle (file object): File handle of the output K file
        :param end_string (str): String that will be used in each line
        iteration and marks the end of the parsing.
        """

        self.qvals = np.array([])

        # Skip subheader
        next(fhandle)

        for line in fhandle:

            if line.strip() != "":
                # We stop the parsing here
                if line.strip().lower().startswith(end_string):
                    return

                # Get indv names if get_indv is True
                if self.get_indv:
                    self.indv.append(line.split()[1])

                # Since the assignment probabilities of each taxon to a
                # specific cluster are not ordered in this output file,
                # a dictionary is create and is populated during the file
                #  parsing. For example, taxonA may have the assignment
                # probability to cluster 3 first, and then to 1, 2 and 4.
                qvalues_dic = defaultdict(float)
                fields = line.strip().split("|")[:-1]

                # Get the assignment probability for the best K assigned to
                # the current taxon
                qvalues_dic[fields[0].split()[3]] = float(fields[0].split()[5])

                # Gather the assignment probabilities for other  K clusters.
                for pop in fields[1:]:
                    # To get the assignment to a particular cluster, we
                    # have to sum all the values for other populations here
                    prob = sum(map(float, pop.split()[-3:]))
                    # pop.split()[1][:-1] gets the cluster number
                    qvalues_dic[int(pop.split()[1][:-1])] = prob

                # Sort the probability assignment values according to cluster
                # positions (e.g. [<cluster 1 prob>, <cluster 2 prob>, ...])
                cl_vals = [vals for k, vals in sorted(qvalues_dic.items())]

                # Here we add the assignment probabilities to the main array.
                # If the array alread exits,use vstack to "append" the values
                # for the current taxon. If it does not exist, create a new
                # array from the values of the first taxon
                try:
                    self.qvals = np.vstack((self.qvals, cl_vals))
                except ValueError:
                    self.qvals = np.array(cl_vals)

    def _parse_nousepopinfo(self, fhandle, end_string):
        """
        Parses Structure results when **not** using the USEPOPINFO flag.

        An example of the Structure output without the USEPOPINFO flag:

        Inferred ancestry of individuals:
        Label (%Miss) Pop:  Inferred clusters
        1  Coc_W.1    (0)    1 :  0.033 0.967
        2 Coc_W.10    (0)    1 :  0.032 0.968
        3 Coc_W.11    (0)    1 :  0.033 0.967
        4 Coc_W.16    (0)    1 :  0.033 0.967

        In this example, K = 2 and the assignment probabilities are ordered
        in the columns [5:]

        :param fhandle (file object): File handle of the output K file
        :param end_string (str): String that will be used in each line
        iteration and marks the end of the parsing.
        """

        self.qvals = np.array([])

        for line in fhandle:

            # Skip empty lines
            if line.strip() != "":

                # We stop parsing here
                if line.strip().lower().startswith(end_string):
                    return

                # Get indv names if get_indv is True
                if self.get_indv:
                    self.indv.append(line.split()[1])
            
                # Get the cluster values
                fields = line.strip().split()
                cl_vals = [float(x) for x in fields[5:]]

                # Here we add the assignment probabilities to the main array.
                # If the array alread exits,use vstack to "append" the values
                # for the current taxon. If it does not exist, create a new
                # array from the values of the first taxon
                try:
                    self.qvals = np.vstack((self.qvals, cl_vals))
                except ValueError:
                    self.qvals = np.array(cl_vals)

    def _parse_structure(self):
        """
        Parses the meanQ array of a single Structure output file
        :return:
        """

        parsing_string = "inferred ancestry of individuals:"
        popinfo_string = "probability of being from assumed " \
                         "population | prob of other pops"
        end_parsing_string = "estimated allele frequencies in each " \
                             "cluster"

        with open(self.file_path) as fh:
            for line in fh:
                # The string that marks the beginning of the parsing was found
                if line.strip().lower().startswith(parsing_string):
                    # Check if the next line has the signature of an output
                    # file generated with the USEPOPINFO flag.
                    if next(fh).lower().startswith(popinfo_string):
                        self._parse_usepopinfo(fh, end_parsing_string)
                        break
                    # THe output file generated was NOT generated with the
                    # USEPOPINFO flag.
                    else:
                        self._parse_nousepopinfo(fh, end_parsing_string)
                        break

        pass

    def _parse_faststructure(self):
        """
        Parses the meanQ array of a single FastStructure output file
        Sets the qvals array, the number of individual taxa (nind)
        and number of clusters (k)
        """

        # Thanks FastStructure, this was really easy.
        self.qvals = np.genfromtxt(self.file_path)

        self.nind, self.k = self.qvals.shape

    def _parse_maverick(self):
        """
        Parses the meanQ array of a single MavericK output file
        :return:
        """

        # Explanation of data import:
        # 1. Import data using genfromtxt numpy method, specifiying the
        #  delimiter and skiping the first header line
        # 2. Remove the first three columns from the array with .T[3:].
        # However, this messes the shape of the structure array, so....
        # 3. We transpose the array so that each row is a taxon and
        # the columns represent the assignment probabilities for each K
        mavarray = np.genfromtxt(self.file_path, delimiter=",",
                                   skip_header=1)
        self.qvals = mavarray.T[3:].T

        if self.get_indv:
            self.indv = list(np.genfromtxt(self.file_path, delimiter=",",
                                           dtype="|U20",
                                           skip_header=1).T[1].T)


class PlotList:
    """
    Main class object that will store multiple PlotK instances for each
    output file provided. The population information is stored in this class
    since it is the same for all PlotK objects. This class also contains
    plotting and array manipulation methods that are necessary to produce
    the output plots
    """

    def __init__(self, ouput_file_list, fmt, popfile=None, indfile=None):
        """
        When a PlotList instance is created, a list of the output files and
        their format must be provided. Optionally, a population file may
        also be provided for additional plot features

        :param ouput_file_list (list): Each element being the path to a
         structure/faststructure/maverick output file (presumably with
         different K values).
        :param fmt (str) ["structure", "faststructure", "maverick"]:
         The format of the k output file.
        :param popfile (str): Path to population file (mutually exclusive
        with indfile).
        :param indfile (str): Path to individual file (mutually exclusive
        with popfile).
        """

        """
        Dictionary attribute that stores the K number
        as key and the corresponding PlotK object as value
        """
        self.kvals = {}

        """
        Sets the maximum K value from the loaded PlotK objects
        """
        self.max_k = 0

        """
        Dictionary that contains metadata for each K key in the main
        kvals dictionary. For now, it only contains the file
        path
        """
        self.metadata = {}

        """
        Sets the format of the output files
        """
        self.fmt = fmt

        """
        Sets attributes that store informtion on the population labels
        .: pops: Stores a list with the population labels only
                 Example: ["PopA", "PopB", "PopC"]
        .: pops_xpos: Stores the position of each population defined
                 in the pops attribute in the x-axis
        .: pops_xrange: Stores the range for each population defined
                 in the pops attribute along the x-axis
        """
        self.pops = []
        self.pops_xpos = []
        self.pops_xrange = []

        """
        Sets the indv attribute that is a basic 1D array that matches
        a taxon/sample name with each row in the PlotK.qvals array
        """
        self.indv = None

        """
        Sets the number of individual samples
        """
        self.number_indv = None

        # Parse each output file and add it to the kvals attribute
        for fpath in ouput_file_list:

            if not popfile and not indfile and self.indv is None:
                # Create PlotK object
                kobj = PlotK(fpath, self.fmt, get_indv=True)
                self.indv = kobj.indv
                self.number_indv = len(self.indv)
            else:
                # Create PlotK object
                kobj = PlotK(fpath, self.fmt)

            self.kvals[kobj.k] = kobj

            # Add metadata for the PlotK object
            self.metadata[kobj.k] = {"filename": fpath}
            # Check maximum K value
            if kobj.k > self.max_k:
                self.max_k = kobj.k

        # If a popfile has been provided, parse it and set the pops attribute
        if popfile:
            self._parse_popfile(popfile)

        # If an indfile
        if indfile:
            self._parse_indfile(indfile)

    def __getattr__(self, item):
        """
        Adds dot notation to get values of the kvals attribute. since the key
        of kvals is an int, the dot notation to access its value must include
        a "k" before the desired k value.
        """
        item = item.replace("k", "")
        try:
            return self.kvals[int(item)]
        except KeyError:
            raise AttributeError

    def __iter__(self):
        """
        PlotList iterates over k value and PlotK objects
        """

        for k, kobj in self.kvals.items():
            yield k, kobj

    def _parse_popfile(self, popfile):
        """
        Parses a population file and sets the pops attribute.

        The popfile is a tsv that consists of three columns:
         .: "Population name"
         .: "Number of individuals in the population"
         .: "Order of the population in the input file"

        Example:
            Location_1  20  1
            Location_2  21  2
            Location_3  11  3

        This means that the first 20 individuals in the output file are from
        location_1 and correspond to the first population in the plot,
        the next 21 individuals (21-42) are from location_2 and correspond
        to the second populations, etc. The order of the populations in the
        structure plot can be re-ordered in the third column.

        The pops attribute that will be set after this method will be a
        a sequence array with the length equal to the number of populations
        where each item will contain the name of the populations and the
        x-axis position of the label

        Example:
            [(Location_1, 10), (Location_2, 31), (Location_3, 47)]

        :param popfile: (str) Path to pop file

        """

        datatype = np.dtype([("popname", "|U20"), ("nind", int),
                             ("original_order", int)])

        poparray = np.genfromtxt(popfile, dtype=datatype)

        # Sort array according to the order in the third column
        poparray.sort(order="original_order")

        pop_sums = np.cumsum(poparray["nind"])

        # Populate pops related attributes
        for p, x in enumerate(poparray):
            # Add population label to list
            self.pops.append(x[0])
            # Add population label position in x-axis
            self.pops_xpos.append(x[1] / 2 + sum(poparray["nind"][:p]))
            # Add population range in the x-axis
            self.pops_xrange.append(
                (pop_sums[p] - poparray["nind"][p], pop_sums[p]))

        self.indv = list(range(self.pops_xrange[-1][-1]))
        self.number_indv = len(self.indv)

    def _parse_indfile(self, indfile):
        """
        Parses an individual file. This should be a .tsv file that has one
        mandatory column and two optional columns:

            .: Column 1 (mandatory): Individual sample/taxon label per row
            .: Column 2 (optional): Population for the corresponding
            sample/taxon
            .: Column 3 (optional): Order of the population in the plot

        Example of a complete indfile:
            TaxonA  Pop1    2
            TaxonB  Pop2    1
            TaxonC  Pop1    2
            ...

        If only the first column is provided, then the xlabels of the
        plot will match each sample/taxon name.

        If the population is provided for each taxon, and there is only ONE
        population, it will be essentially the same as providing only the
        sample/taxon names column.

        If the multiple populations are provided in the second column, the
        self.pops attribute will be set like in _parse_popfile. Unless
        the population order is specified in the third column, we assume the
        same order that the populations are specified in the indfile.

        :param indfile: (str) Path to indfile
        """

        # Import infile as array. dtype is set to None to allow automatic
        # detection of dtype for each column (since the number of columns
        # is variable)
        indarray = np.genfromtxt(indfile, dtype="|U20")

        # Now we evaluate the the information contained in the indfile
        # If only one column is present, we set self.indv and nothing more
        if len(indarray.shape) == 1:
            self.indv = indarray
            self.number_indv = len(self.indv)
            return

        # If specifically two columns were specified, the second column
        # contains the population information.
        elif indarray.shape[1] >= 2:

            # Get the populations
            npops = sorted((set(indarray[:, 1])))

            self.indv = indarray[:, 0]
            self.number_indv = len(self.indv)

            # If only one population, set only self.indv
            if len(npops) == 1:
                return

            # If there are multiple populations
            else:

                # Sort the individuals according to the order provided in the
                # third column, if it is available
                if indarray.shape[1] == 3:
                    indarray = indarray[indarray[:, 2].argsort()]
                    # Sort the population list according to the new order
                    npops = list(OrderedDict.fromkeys(indarray[:, 1]))

                else:
                    # Sort the individuals alphabetically per population if no
                    # order column was provided
                    indarray = indarray[indarray[:, 1].argsort()]

                # Set self.pops attribute
                pop_counts = Counter(indarray[:, 1])
                pop_sums = np.cumsum([np.count_nonzero(indarray == x)
                                      for x in npops])

                # Populate pops related attributes
                for p, pop in enumerate(npops):
                # Add population label to list
                    self.pops.append(pop)
                    self.pops_xpos.append(pop_sums[p] - pop_counts[pop] / 2)
                    self.pops_xrange.append(
                        (pop_sums[p] - pop_counts[pop], pop_sums[p]))

    def plotk(self, kvals, output_dir):
        """
        Generates a plot for each K value in kvals. These kvals must be
        present in the kvals dictionary attribute. If only one k value is
        provided, this generates a single standard plot. If multiple kvals
        are provided, it generates multiple subplots along a vertical
        axis with a shared x-axis and legend.

        ::NOTE:: USING INDIVIDUAL LABELS VS. POPULATION LABELS
        During the parsing of the popfile or indfile, it is possible
        that the PlotList attributes "self.indv" and "self.pops" are set.
            :: Whenver self.pops is set, the population labels will take
            precedence over the individual labels on the x-axis of the plot.
            However, if self.indv is provided along with self.pops, it will
            be possible to add the sample name for the on_hover effects of
            the plot.
            :: If ONLY self.indv is set, then the x-axis labels will be
            populated with the individual sample names.

        :param kvals: (sequence/iterable) A sequence of the K values that
        should be plotted.
        :param output_dir: (str) Path to the directory where the plots will
        be generated
        """

        # Get number of plots (confirm the kvals are valid before)
        nplots = len([x for x in kvals if int(x) in self.kvals])

        # Set the figure object with the subplots and their titles already
        # specified
        fig = tools.make_subplots(
            rows=nplots,
            cols=1,
            shared_xaxes=True,
            subplot_titles=[basename(self.kvals[k].file_path) for k in kvals
                            if k in self.kvals],
            vertical_spacing=0.05)

        shape_list = []
        # Attributes specific for when population labels are provided
        if self.pops:
            # Variable that will store the coordinates of the population
            # boundary # vertical lines
            pop_lines = list(OrderedDict.fromkeys(
                [x for y in self.pops_xrange for x in y]))[1:-1]
            # Stores the information on the population vertical lines
            # that will be passed to the figure layout

        # Make sure that the highest K is processed first
        for j, k in enumerate(sorted(
                [x for x in kvals if x in self.kvals], reverse=True)):

            # Fetch PlotK object that will be plotted
            kobj = self.kvals[k]

            # Iterate over each meanQ column (corresponding to each cluster)
            for p, i in enumerate(kobj.qvals.T):

                # Create Bar trace for each cluster
                current_bar = go.Bar(
                    # Set xticks
                    x=self.indv,
                    # Set yaxis values
                    y=i,
                    # Name of the cluster for the legend
                    name="K {}".format(p),
                    # Set equal cluster indexes to the same group. This
                    # ensures that K3, for example, has the same legend
                    # reference across all subplots
                    legendgroup="group_{}".format(p),
                    # Set hover text information
                    text=["Assignment: {}%".format(x * 100) for x in i],
                    # Customization of bars
                    marker=dict(
                        #TODO: Only 12 colors supported for now
                        color=c[p],
                        line=dict(
                            color='grey',
                            width=2,
                        )),
                    # Only the first (highest K) plot will have a legend
                    showlegend=True if j == 0 else False)

                # Append the current barplot to the respective subplot
                fig.append_trace(current_bar, j + 1, 1)

            # Add population boundary lines
            if self.pops:
                for x in pop_lines:
                    line_data = {
                        "type": "line",
                        "x0": x - .5,
                        "y0": 0,
                        "x1": x - .5,
                        "y1": 1,
                        # Add reference to the subplot where this line will be
                        # added
                        "yref": "y{}".format(j + 1),
                        "line": {"width": 3}}
                    shape_list.append(line_data)

            # Disable yticks for current subplot
            fig["layout"]["yaxis{}".format(j + 1)].update(
                showticklabels=False)

            # Add frames to each subplot
            shape_list.append(
                {"type": "line", "x0": -0.5, "y0": 0,
                 "x1": self.number_indv - 0.5, "y1": 0,
                 "yref": "y{}".format(j + 1), "line": {"width": 3}})
            shape_list.append(
                {"type": "line", "x0": -0.5, "y0": 0, "x1": -0.5, "y1": 1,
                 "yref": "y{}".format(j + 1), "line": {"width": 3}})
            shape_list.append(
                {"type": "line", "x0": -0.5, "y0": 1,
                 "x1": self.number_indv - 0.5, "y1": 1,
                 "yref": "y{}".format(j + 1), "line": {"width": 3}})
            shape_list.append(
                {"type": "line", "x0": self.number_indv - 0.5, "y0": 0,
                 "x1": self.number_indv - 0.5, "y1": 1,
                 "yref": "y{}".format(j + 1), "line": {"width": 3}})

        if self.pops:
            # Customization of x-axis with population labels
            xdata = {"range": [-0.6, self.number_indv - 0.4],
                     "ticks": "",
                     "showticklabels": True,
                     "mirror": True,
                     "ticktext": self.pops,
                     "tickvals": self.pops_xpos,
                     "tickangle": -45,
                     "tickfont": dict(size=22,
                                       color='black')}

            # Automatic setting of the bottom margin to accomodate larger
            # population labels
            bmargin = 14.5 * max([len(x) for x in self.pops])

        else:
            xdata = {"range": [-0.6, self.number_indv - 0.4],
                     "showticklabels": True,
                     "mirror": True,
                     "tickangle": -45,
                     "tickfont": dict(size=14,
                                       color='black')}

            # Automatic setting of the bottom margin to accommodate larger
            # individual sample names
            bmargin = 14.5 * max([len(x) for x in self.indv])

        bmargin = bmargin if bmargin >= 80 else 80

        # Update layout with population boundary shapes
        fig["layout"].update(shapes=shape_list)  # Update first xaxis
        fig["layout"]["xaxis1"].update(**xdata)

        fig["layout"].update(barmode="stack",
                              bargap=0,
                              margin={"b": bmargin},
                              legend={"x": 1, "y": 0.5})

        # Determine file name. If a single K value is provided, then
        # adapt from the ouptut name of that K value file.
        # If there are multiple K vales,the filename will reflect the
        # K values included.
        if len(kvals) == 1:
            kfile = self.kvals[kvals[0]].file_path
            filename = splitext(basename(kfile))[0]
        else:
            filename = "ComparativePlot_{}".format("-".join(
                [str(x) for x in kvals]))
        filepath = join(output_dir, filename)

        pdiv = plot(fig, include_plotlyjs=False, output_type='div')
        # Remove plotly div
        pdiv = pdiv.replace(', {"showLink": true, "linkText": '
                             '"Export to plot.ly"}', '')

        # Create html file
        with open(filepath, "w") as fh:
            fh.write(ploty_html(pdiv))

    def plotk_static(self, kval, output_dir):
        """

        """

        qvalues = self.kvals[kval].qvals

        plt.style.use("ggplot")

        numinds = self.number_indv

        clist = [[i / 255. for i in x] for x in cl.to_numeric(c)]

        # Update plot width according to the number of samples
        plt.rcParams["figure.figsize"] = (8 * numinds * .03, 2.64)

        fig = plt.figure()
        axe = fig.add_subplot(111, xlim=(-.5, numinds - .5), ylim=(0, 1))

        for i in range(qvalues.shape[1]):
            # Get bar color. If K exceeds the 12 colors, generate random color
            try:
                clr = clist[i]
            except IndexError:
                clr = np.random.rand(3, 1)

            if i == 0:
                axe.bar(range(numinds), qvalues[:, i], facecolor=clr,
                        edgecolor="grey", width=1)
                former_q = qvalues[:, i]
            else:
                axe.bar(range(numinds), qvalues[:, i], bottom=former_q,
                        facecolor=clr, edgecolor="grey", width=1)
                former_q = former_q + qvalues[:, i]

        # Annotate population info
        if self.pops:

            pop_lines = list(OrderedDict.fromkeys(
                [x for y in self.pops_xrange for x in y]))[1:-1]

            for pl in pop_lines:

                # Add population delimiting lines
                plt.axvline(x=pl - 0.5, linewidth=1.5, color="black")

            for p, pos in enumerate(self.pops_xpos):
                axe.text(pos, -0.05, self.pops[p],
                         rotation=45, va="top", ha="right", fontsize=16,
                         weight="bold")
        else:

            for pos in range(self.number_indv):
                axe.text(pos, -0.05, self.indv[pos],
                         rotation=45, va="top", ha="right", fontsize=10)

        for axis in ["top", "bottom", "left", "right"]:
            axe.spines[axis].set_linewidth(2)
            axe.spines[axis].set_color("black")

        plt.yticks([])
        plt.xticks([])

        kfile = self.kvals[kval].file_path
        filename = splitext(basename(kfile))[0]
        filepath = join(output_dir, filename)

        plt.savefig("{}.svg".format(filepath), bbox_inches="tight")


def main(result_files, fmt, outdir, bestk=None, popfile=None, indfile=None):
    """
    Wrapper function that generates one plot for each K value.
    :return:
    """

    klist = PlotList(result_files, fmt, popfile=popfile, indfile=indfile)

    # Plot all K files individually
    for k, kobj in klist:

        if k >= 1:
            klist.plotk([k], outdir)
            klist.plotk_static(k, outdir)

    # If a sequence of multiple bestk is provided, plot all files in a single
    # plot
    if bestk:
        bestk = [x for x in bestk if x >= 1]
        klist.plotk(bestk, outdir)

if __name__ == "__main__":
    kdir = "/home/diogo/Diogo/Science/PhD/Tasks/Hemileia_RADs/" \
           "2_RADs_full/Assembly/ipyrad/Ingroup/Var1/Analyses/" \
           "Structure/RandSNP/R2/"
    files = ["HvFullSample_ingroup_v1_MM50_mafRandSNP.5.meanQ",
             "HvFullSample_ingroup_v1_MM50_mafRandSNP.4.meanQ",
             "HvFullSample_ingroup_v1_MM50_mafRandSNP.3.meanQ",
             "HvFullSample_ingroup_v1_MM50_mafRandSNP.2.meanQ"]
    indfile = join(kdir, "indfile2.txt")
    kfiles = [join(kdir, f) for f in files]

    main(kfiles, "faststructure", "./", indfile=indfile)
