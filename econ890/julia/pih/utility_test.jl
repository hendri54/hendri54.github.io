using Random, Test

# This is one reason why packages work better.
include("utility.jl");
using .UtilityFunctions

# We are testing a common interface for every utility function.
function util_test(u :: AbstractUtility)
    # When you generate random numbers, always set the seed first.
    rng = MersenneTwister(23);
    @testset "$u" begin
        betaR = 1.03;
        c = 1.0 .+ rand(rng, 4,3,2);
        util = utility(u, c);
        @test size(util) == size(c);

        # inverse utility = consumption
        invUtil = inv_utility(u, util);
        @test isapprox(c, invUtil);

        # Test marginal utility by perturbation
        mu = marg_utility(u, c);
        @test all(mu .> 0.0)
        @test size(mu) == size(c)
        dc = 1e-7;
        util2 = utility(u, c .+ dc);
        mu2 = (util2 .- util) ./ dc;
        # Precision is not perfect here
        @test isapprox(mu, mu2, rtol = 1e-4);
        invMu = inv_marg_utility(u, mu);
        @test isapprox(c, invMu)

        # For consumption growth, use Euler deviation
        cGrowth = c_growth(u, betaR);
        T = 7;
        cV = cGrowth .^ (1 : T);
        devV = euler_dev(u, cV, betaR);
        @test all(abs.(devV .< 1e-5))
    end
end

@testset "Utility" begin
    for u ∈ (
        UtilityLog(),
        UtilityCRRA(2.0)
        )

        util_test(u);
    end
end

# ------------