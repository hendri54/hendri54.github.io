# PIH model: Using a `Model` object.
# Now packaged in a module. Otherwise reloading gives errors that structs are redefined.

module PIH2

export Model, pih2, euler_dev, cons_path
# For solving by interpolation
export solve_by_interpolation, solve_by_root_finding, pv_cons, present_value
# Need to also export items from utility function.
# Those should be in their own module, but we kept it "simple".
export AbstractUtility, UtilityLog, UtilityCRRA

# Code for utility functions
include("utility.jl");

struct Model
    Y :: Float64
    R :: Float64
    T :: Int
    beta :: Float64
    u :: AbstractUtility
end

betar(m :: Model) = m.beta * m.R;

# g + g^2 + ... + g^(T-1)
pvfactor(g, T) = (g ^ T - 1.0) / (g - 1.0);

present_value(xV, R) = sum(xV ./ (R .^ (0 : (length(xV)-1))));

euler_dev(m :: Model, ctV) = euler_dev(m.u, ctV, betar(m));


# This solves for c(t)
function pih2(m :: Model)
    g = c_growth(m.u, betar(m));
    c1 = m.Y / pvfactor(g / m.R, m.T);
    # This is still no good - mixing levels of abstraction.
    ctV = c1 .* (g .^ (0 : (m.T - 1)));
    return ctV
end


## --------  Solve by interpolation and shooting

function cons_path(m :: Model, cT :: Float64)
    ctV = zeros(m.T);
    ctV[m.T] = cT;
    for t = m.T : -1 : 2
        ctV[t-1] = ctV[t] / c_growth(m.u, betar(m));
    end
    return ctV
end

function pv_cons(m :: Model, cT :: Float64)
    ctV = cons_path(m, cT);
    pv = present_value(ctV, m.R);
end

function solve_by_interpolation(m)
    n = 100;
    cGridV = LinRange(0.01 * m.Y, 0.5 * m.Y, n);
    # A comprehension
    pvV = [pv_cons(m, cT)  for cT ∈ cGridV];
    @assert ((pvV[1] < m.Y)  &&  (pvV[n] > m.Y))  "Search range too narrow";

    # Interpolate by hand
    cT = interpolate(pvV, cGridV, m.Y);
    @assert cT > 0.0

    # Self-test
    @assert isapprox(pv_cons(m, cT), m.Y, rtol = 1e-4)  "B.C. violated"

    ctV = cons_path(m, cT);
    return ctV
end

function interpolate(xV, yV, x0)
    idx = findfirst(xV .> x0) - 1;
    @assert idx > 0
    y = yV[idx] + (yV[idx+1] - yV[idx]) * (x0 - xV[idx]) / (xV[idx+1] - xV[idx]);
    @assert yV[idx+1] >= y >= yV[idx]
    return y
end

## ----------  Root finding

# This is poor style. All of the `using` statements should be at the top of the file.
# But I want to make clear what we are adding to the project as we develop it step by step.
using Roots

function solve_by_root_finding(m)
    # This is a closure
    # The same as using the anonymous function 
    #   `cT -> budget_surplus(m, cT)`
    f(cT) = budget_surplus(m, cT);
    cT = find_zero(f, (0.01*m.Y, 0.5*m.Y), Bisection());

    # Self-test
    @assert isapprox(pv_cons(m, cT), m.Y, rtol = 1e-4)  "B.C. violated"

    ctV = cons_path(m, cT);
    return ctV
end

budget_surplus(m :: Model, cT) = m.Y - pv_cons(m, cT);

end # module

# ----------