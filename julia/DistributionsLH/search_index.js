var documenterSearchIndex = {"docs":
[{"location":"index.html#DistributionsLH","page":"DistributionsLH","title":"DistributionsLH","text":"","category":"section"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"This package makes ModelObjects for random variables drawn from select distributions.","category":"page"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"For the most part, this just wraps distributions from Distributions.jl into ModelObjects from ModelParams so that the parameters can be calibrated conveniently and so that fixed properties can be set using switches objects.","category":"page"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"There are also extensions to the distributions in Distributions.jl. For example, the Beta distribution is defined over an arbitrary range rather than [0, 1].","category":"page"},{"location":"index.html#Generic-interface","page":"DistributionsLH","title":"Generic interface","text":"","category":"section"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"Each distribution implements the following","category":"page"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"init_distribution\ndraw\nscale_normal_draws\nquantiles\nmin_value\nmax_value\ncheck_draws","category":"page"},{"location":"index.html#DistributionsLH.init_distribution","page":"DistributionsLH","title":"DistributionsLH.init_distribution","text":"init_distribution(objId, switches)\n\nInitialize a distribution from its switches.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.draw","page":"DistributionsLH","title":"DistributionsLH.draw","text":"draw(distrib, nDims, rng)\ndraw(distrib, rng)\n\nDraw from the distribution.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.scale_normal_draws","page":"DistributionsLH","title":"DistributionsLH.scale_normal_draws","text":"scale_normal_draws(b, inM)\n\n\nConverts N(0,1) draws into the specified distribution.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.quantiles","page":"DistributionsLH","title":"DistributionsLH.quantiles","text":"quantiles(distrib, pctV)\n\nQuantiles.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.min_value","page":"DistributionsLH","title":"DistributionsLH.min_value","text":"min_value(distrib)\n\nMinimum value (if any).\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.max_value","page":"DistributionsLH","title":"DistributionsLH.max_value","text":"max_value(distrib)\n\nMaximum value (if any).\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.check_draws","page":"DistributionsLH","title":"DistributionsLH.check_draws","text":"check_draws(distrib, drawM)\n\nCheck draws against bounds (if any) and Inf values.\n\n\n\n\n\n","category":"function"},{"location":"index.html#Uniform-distribution","page":"DistributionsLH","title":"Uniform distribution","text":"","category":"section"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"AbstractUniformSwitches\nAbstractUniform\nUniform\nUniformFixedBounds\nUniformCenteredSwitches\nUniformCentered\ninit_uniform","category":"page"},{"location":"index.html#DistributionsLH.AbstractUniformSwitches","page":"DistributionsLH","title":"DistributionsLH.AbstractUniformSwitches","text":"Abstract type for switches governing how Uniform distributions are parameterized.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.AbstractUniform","page":"DistributionsLH","title":"DistributionsLH.AbstractUniform","text":"Abstract Uniform type. \n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.Uniform","page":"DistributionsLH","title":"DistributionsLH.Uniform","text":"Unform distribution on interval xMin + [0, xRange].\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.UniformFixedBounds","page":"DistributionsLH","title":"DistributionsLH.UniformFixedBounds","text":"UniformFixedBounds(objId, lb, ub)\n\n\nUniform distribution with fixed bounds (not calibrated).\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.UniformCenteredSwitches","page":"DistributionsLH","title":"DistributionsLH.UniformCenteredSwitches","text":"Switches for Uniform distribution that is centered around a mean.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.UniformCentered","page":"DistributionsLH","title":"DistributionsLH.UniformCentered","text":"Unform distribution on interval xMean +/- 0.5 * xRange.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.init_uniform","page":"DistributionsLH","title":"DistributionsLH.init_uniform","text":"init_uniform(objId, switches)\n\n\nConstruct a Uniform distribution from its switches.\n\n\n\n\n\n","category":"function"},{"location":"index.html#Beta-distribution","page":"DistributionsLH","title":"Beta distribution","text":"","category":"section"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"BetaSwitches\nBeta\ninit_beta","category":"page"},{"location":"index.html#DistributionsLH.BetaSwitches","page":"DistributionsLH","title":"DistributionsLH.BetaSwitches","text":"Switches for default Beta distribution object.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.Beta","page":"DistributionsLH","title":"DistributionsLH.Beta","text":"Beta marginal distribution. Characterized by lower bound, upper bound, and Beta parameters alpha and beta. Cannot store the Beta distribution in the object because its parameters are not known.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.init_beta","page":"DistributionsLH","title":"DistributionsLH.init_beta","text":"init_beta(objId, switches)\n\n\nConstruct a Uniform distribution from its switches.\n\n\n\n\n\n","category":"function"},{"location":"index.html#Multivariate-Normal-Distribution","page":"DistributionsLH","title":"Multivariate Normal Distribution","text":"","category":"section"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"The main purpose is to be able to draw random variables from the \"weight matrix\" which is basically a lower triangular decomposition of the covariance matrix, but with ones on the diagonal. The draws are then scaled to match the target means and standard deviations of the marginals.","category":"page"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"Also computes conditional distributions.","category":"page"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"MvNormalLHSwitches\nMvNormalLH\ncov_matrix\ncheck_cov_matrix\ndraw_from_weights\ncheck_weight_matrix\nconditional_distrib\ncond_mean_weights","category":"page"},{"location":"index.html#DistributionsLH.MvNormalLHSwitches","page":"DistributionsLH","title":"DistributionsLH.MvNormalLHSwitches","text":"Switches used to construct Multivariate Normal object.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.MvNormalLH","page":"DistributionsLH","title":"DistributionsLH.MvNormalLH","text":"Multivariation Normal object. \n\nThis is a ModelObject but currently does not support calibrating parameters.\n\n\n\n\n\n","category":"type"},{"location":"index.html#DistributionsLH.cov_matrix","page":"DistributionsLH","title":"DistributionsLH.cov_matrix","text":"Make cov matrix from weight matrix.\n\nThe weight matrix is lower triangular with ones on the diagonal.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.check_cov_matrix","page":"DistributionsLH","title":"DistributionsLH.check_cov_matrix","text":"Check that a covariance matrix is valid for a given MvNormalLH object.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.draw_from_weights","page":"DistributionsLH","title":"DistributionsLH.draw_from_weights","text":"draw_from_weights(m, wtM, nObs, rng)\n\n\nDraw random variables given the weight matrix. Returns Matrix by observation, variable.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.check_weight_matrix","page":"DistributionsLH","title":"DistributionsLH.check_weight_matrix","text":"check_weight_matrix(m, wtM)\n\n\nCheck that weight matrix is valid.\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.conditional_distrib","page":"DistributionsLH","title":"DistributionsLH.conditional_distrib","text":"Compute conditional distribution of a set of variables, given the others For Multiple sets of conditioning observations\n\nArguments\n\ncovM   covariance matrix\nidx2V   indices of variables on which we condition\nvalue2M[observation, variable]   their values\n\nOutputs\n\ncondMeanM[observation, variable]\ncondStdV(variable)   conditional means and std of each variable, given all others   for those not in idx2V\ncondCovM(variable, variable)   conditional covariance; for those not in idx2\n\n\n\n\n\n","category":"function"},{"location":"index.html#DistributionsLH.cond_mean_weights","page":"DistributionsLH","title":"DistributionsLH.cond_mean_weights","text":"cond_mean_weights(m, idx2V, covM)\n\n\nWeights of conditioning variables for conditional means: sigma12/sigma22. Such that \n\n`conditional mean = mu1 + weights * (value2 - mu2)`\n\nOutputs\n\nwtM   n1 x n2 matrix of weights   each row gives the weights for a \"dependent\" variable\n\n\n\n\n\n","category":"function"},{"location":"index.html","page":"DistributionsLH","title":"DistributionsLH","text":"","category":"page"}]
}