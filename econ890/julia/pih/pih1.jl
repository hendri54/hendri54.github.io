# PIH model: simplest approach
# This is not good code, but it runs.
# We will improve later.

# This solves for c(t) in closed form
# Note that unicode characters, such as β, can be typed as `\beta + tab`.
function pih1(Y, R, T, β, σ)
    # A little self-testing does not hurt.
    @assert Y > 0.0  "Income must be positive"
    consGrowth = (β * R) ^ (1.0 / σ);
    # Note that this should be reusable function
    pvFactor = ((consGrowth / R) ^ T - 1.0) / ((consGrowth / R) - 1.0);
    c1 = Y / pvFactor;
    ctV = c1 .* (consGrowth .^ (0 : (T-1)));
    return ctV
end

# Check that it works...
# This is in a function, so we don't pollute `Main`.
function run_pih1()
    Y = 10.0;
    R = 1.05;
    T = 9;
    β = 0.98;
    σ = 2.0;

    @show pih1(Y, R, T, β, σ)
end


## ----------  Testing this
# This would usually be in a different file, of course.

using Test

# Again, in a function, so there are no side-effects.
# We can obtain a fairly complete test by checking that the definition of a solution is satisfied:
# - budget constraint
# - Euler equation
function pih_test()
    Y = 10.0;
    R = 1.05;
    T = 9;
    β = 0.98;
    σ = 2.0;
    ctV = pih1(Y, R, T, β, σ);

    @testset "PIH" begin
        @test all(ctV .> 0.0)
        @test ctV isa Vector{Float64}
        @test length(ctV) == T

        # Euler equation
        muV = ctV .^ (-σ);
        eeDevV = muV[1 : (T-1)] ./ muV[2 : T] .- β * R;
        @test all(abs.(eeDevV .< 1e-6))

        # Budget constraint
        pvC = sum(ctV ./ (R .^ (0 : (T-1))));
        @test abs(pvC - Y) < 1e-6
    end
end

pih_test()

# ----------