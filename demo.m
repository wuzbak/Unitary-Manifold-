% demo.m — Quantum Gate Optimization Demo
%
% Demonstrates Riemannian gradient descent on the unitary group U(n) to
% recover a target gate (CNOT or SWAP) from a random initial unitary.
%
% Usage (MATLAB / Octave):
%   demo          % runs both CNOT and SWAP optimizations
%
% Algorithm
% ---------
% Cost function   : C(U) = (1/2) * ||U - U_target||_F^2
% Euclidean grad  : nabla C = U - U_target
% Riemannian grad : G_skew  = skew_herm(U' * nabla C)   (tangent at U)
% Retraction      : U_new   = U * expm(-lr * G_skew)    (stays on U(n))
%
% Validation
% ----------
% After each optimization run, check_unitarity() verifies
%   ||U'*U - I||_F < epsilon
%
% License: MIT — see LICENSE
% Author : ThomasCory Walker-Pearson, 2026

function demo()

    fprintf('=============================================\n');
    fprintf('  Quantum Gate Optimization Demo (demo.m)   \n');
    fprintf('=============================================\n\n');

    % ------------------------------------------------------------------ %
    % Target gates (standard computational-basis ordering)               %
    % ------------------------------------------------------------------ %

    % CNOT  (control qubit = row 1, target qubit = row 2)
    CNOT = [1 0 0 0;
            0 1 0 0;
            0 0 0 1;
            0 0 1 0];

    % SWAP
    SWAP = [1 0 0 0;
            0 0 1 0;
            0 1 0 0;
            0 0 0 1];

    epsilon = 1e-6;   % unitarity tolerance

    % ------------------------------------------------------------------ %
    % Optimize towards CNOT                                               %
    % ------------------------------------------------------------------ %
    fprintf('--- Optimizing towards CNOT gate ---\n');
    [U_cnot, hist_cnot] = optimize_gate(CNOT, 'CNOT', 0.1, 1000, 1e-10);
    check_unitarity(U_cnot, 'CNOT', epsilon);
    fprintf('\n');

    % ------------------------------------------------------------------ %
    % Optimize towards SWAP                                               %
    % ------------------------------------------------------------------ %
    fprintf('--- Optimizing towards SWAP gate ---\n');
    [U_swap, hist_swap] = optimize_gate(SWAP, 'SWAP', 0.1, 1000, 1e-10);
    check_unitarity(U_swap, 'SWAP', epsilon);
    fprintf('\n');

    % ------------------------------------------------------------------ %
    % Optional: plot convergence if graphics are available               %
    % ------------------------------------------------------------------ %
    try
        figure('Name', 'Gate Optimization Convergence');
        semilogy(hist_cnot, 'b-',  'LineWidth', 1.5, 'DisplayName', 'CNOT'); hold on;
        semilogy(hist_swap, 'r--', 'LineWidth', 1.5, 'DisplayName', 'SWAP');
        xlabel('Iteration');
        ylabel('Cost  C(U) = \frac{1}{2}||U - U_{target}||_F^2');
        title('Riemannian Gradient Descent on U(4)');
        legend('Location', 'best');
        grid on;
        fprintf('Convergence plot displayed.\n');
    catch
        % Non-interactive environment — skip plotting silently.
    end

end % function demo


% ===================================================================== %
%  optimize_gate                                                         %
% ===================================================================== %
function [U, cost_history] = optimize_gate(U_target, name, lr, max_iter, tol)
% OPTIMIZE_GATE  Riemannian gradient descent to find U ≈ U_target.
%
%   [U, cost_history] = optimize_gate(U_target, name, lr, max_iter, tol)
%
%   Inputs
%   ------
%   U_target  : n×n unitary target matrix
%   name      : string label for display
%   lr        : learning rate (step size)
%   max_iter  : maximum number of iterations
%   tol       : cost tolerance for early stopping
%
%   Outputs
%   -------
%   U            : optimized n×n unitary matrix
%   cost_history : vector of cost values per iteration

    n = size(U_target, 1);

    % Random initial unitary via QR decomposition of a complex Gaussian matrix
    [U, ~] = qr(randn(n) + 1i * randn(n));

    cost_history = zeros(max_iter, 1);
    converged_iter = max_iter;

    for k = 1:max_iter

        % Euclidean gradient: dC/dU* = U - U_target
        grad_euc = U - U_target;

        % Project onto tangent space of U(n) at U:
        %   G     = U' * grad_euc         (n×n complex matrix)
        %   G_skew = (G - G') / 2         (skew-Hermitian part)
        G       = U' * grad_euc;
        G_skew  = (G - G') / 2;

        % Retraction: geodesic step via matrix exponential
        U = U * expm(-lr * G_skew);

        % Cost  C(U) = (1/2) * ||U - U_target||_F^2
        diff           = U - U_target;
        cost_history(k) = 0.5 * real(trace(diff' * diff));

        % Progress reporting every 100 iterations
        if mod(k, 100) == 0
            fprintf('  [%s]  iter %4d : cost = %.4e\n', name, k, cost_history(k));
        end

        % Early stopping
        if cost_history(k) < tol
            converged_iter = k;
            fprintf('  [%s]  Converged at iteration %d  (cost = %.4e)\n', ...
                    name, k, cost_history(k));
            break;
        end

    end

    cost_history = cost_history(1:converged_iter);

    if converged_iter == max_iter
        fprintf('  [%s]  Reached max_iter=%d  (final cost = %.4e)\n', ...
                name, max_iter, cost_history(end));
    end

end % function optimize_gate


% ===================================================================== %
%  check_unitarity                                                       %
% ===================================================================== %
function pass = check_unitarity(U, name, epsilon)
% CHECK_UNITARITY  Verify that U is numerically unitary.
%
%   pass = check_unitarity(U, name, epsilon)
%
%   Tests the Frobenius-norm condition
%       ||U' * U  -  I||_F  <  epsilon
%
%   Inputs
%   ------
%   U       : n×n matrix to validate
%   name    : string label for display
%   epsilon : tolerance (e.g. 1e-6)
%
%   Output
%   ------
%   pass : logical true if the condition is satisfied, false otherwise

    n   = size(U, 1);
    err = norm(U' * U - eye(n), 'fro');

    if err < epsilon
        fprintf('  [PASS]  %s  ||U^dagger U - I||_F = %.3e  <  eps = %.0e\n', ...
                name, err, epsilon);
        pass = true;
    else
        fprintf('  [FAIL]  %s  ||U^dagger U - I||_F = %.3e  >=  eps = %.0e\n', ...
                name, err, epsilon);
        pass = false;
    end

end % function check_unitarity
