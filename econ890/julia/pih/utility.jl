abstract type AbstractUtility end

# Euler equation deviation. Generic!
function euler_dev(
    u :: AbstractUtility, 
    cV :: AbstractVector{Float64}, 
    betaR :: Float64
    )
    muV = marg_utility(u, cV);
    T = length(cV);
    devV = muV[1 : (T-1)] ./ muV[2 : T] .- betaR;
    return devV
end


## ----------  Log

struct UtilityLog <: AbstractUtility end

# Note the broadcasting dot. This now works for scalars and arrays.
utility(u :: UtilityLog, c) = log.(c);
marg_utility(u :: UtilityLog, c) = 1.0 ./ c;
inv_utility(u :: UtilityLog, util) = exp.(util);
inv_marg_utility(u :: UtilityLog, mu) = 1.0 ./ mu;
c_growth(u :: UtilityLog, betaR) = betaR;


## -----------  CRRA

struct UtilityCRRA <: AbstractUtility 
    sigma :: Float64
end

utility(u :: UtilityCRRA, c) = (c .^ (1.0 - u.sigma)) ./ (1.0 - u.sigma) .- 1.0;
marg_utility(u :: UtilityCRRA, c) = c .^ (-u.sigma);
inv_utility(u :: UtilityCRRA, util) = ((util .+ 1.0) .* (1.0 - u.sigma)) .^ (1.0 / (1.0 - u.sigma));
inv_marg_utility(u :: UtilityCRRA, mu) = mu .^ (-1.0 / u.sigma);
c_growth(u :: UtilityCRRA, betaR) = betaR .^ (1.0 / u.sigma);


# -------------