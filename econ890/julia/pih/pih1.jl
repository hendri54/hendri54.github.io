# PIH model: simplest approach

# This solves for c(t)
function pih1(Y, R, T, pBeta, pSigma)
    g = (pBeta * R) ^ (1.0 / pSigma);
    pvFactor = ((g / R) ^ T - 1.0) / ((g / R) - 1.0);
    c1 = Y / pvFactor;
    ctV = c1 .* (g .^ (0 : (T-1)));
    return ctV
end

# Check that it works...
# This is in a function, so we don't pollute `Main`.
function run_pih1()
    Y = 10.0;
    R = 1.05;
    T = 9;
    pBeta = 0.98;
    pSigma = 2.0;

    @show pih1(Y, R, T, pBeta, pSigma)
end


## ----------  Testing this

using Test

# Again, in a function, so there are no side-effects.
function pih_test()
    Y = 10.0;
    R = 1.05;
    T = 9;
    pBeta = 0.98;
    pSigma = 2.0;
    ctV = pih1(Y, R, T, pBeta, pSigma);

    @testset "PIH" begin
        @test all(ctV .> 0.0)
        @test ctV isa Vector{Float64}
        @test length(ctV) == T

        # Euler equation
        muV = ctV .^ (-pSigma);
        eeDevV = muV[1 : (T-1)] ./ muV[2 : T] .- pBeta * R;
        @test all(abs.(eeDevV .< 1e-6))

        # Budget constraint
        pvC = sum(ctV ./ (R .^ (0 : (T-1))));
        @test abs(pvC - Y) < 1e-6
    end
end

pih_test()

# ----------