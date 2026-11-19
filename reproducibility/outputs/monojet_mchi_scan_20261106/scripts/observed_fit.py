"""One-sided observed CLs with Poisson bins and correlated Gaussian constraints."""
from dataclasses import dataclass
from math import erfc, sqrt

import numpy as np


@dataclass(frozen=True)
class Profile:
    deviance: float
    mean: np.ndarray
    slope: float
    active_bins: int


class ObservedFit:
    def __init__(self, data, background, covariance):
        self.data = np.asarray(data, dtype=float)
        self.b = np.asarray(background, dtype=float)
        self.covariance = covariance
        assert self.b.shape == self.data.shape and np.all(self.data>0) and np.all(self.b>0)
        self.chol = np.linalg.cholesky(covariance)
        self.identity = np.eye(len(self.data))

    def _poisson_profile(self, center, chol):
        n = self.data
        latent = np.zeros_like(n)

        def deviance(z, mean):
            relative = (mean-n)/n
            return float(2*np.sum(n*(relative-np.log1p(relative))) + z@z)

        for _ in range(40):
            mean = center+chol@latent
            score = 1-n/mean
            gradient = latent+chol.T@score
            if np.max(np.abs(gradient))<1e-7:
                return deviance(latent,mean),mean,score
            hessian = self.identity+chol.T@((n/mean**2)[:,None]*chol)
            direction = np.linalg.solve(hessian,-gradient)
            response = chol@direction
            current = deviance(latent,mean)
            step = 1.
            for _ in range(28):
                trial_mean = mean+step*response
                if np.all(trial_mean>0) and deviance(latent+step*direction,trial_mean)<=current+1e-10:
                    break
                step *= .5
            else:
                raise RuntimeError("Observed profile line search failed")
            latent += step*direction
        raise RuntimeError("Observed profile did not converge")

    def profile(self, nu, signal, signal_cov=None):
        if signal_cov is None or nu==0:
            deviance,mean,score = self._poisson_profile(self.b+nu*signal,self.chol)
            return Profile(deviance,mean,float(2*score@signal),0)

        # At a fixed active set, conditioning the signal Gaussian on zero
        # yields gives a lower-dimensional Gaussian plus a constant penalty.
        active = []
        for _ in range(2*len(signal)):
            if active:
                columns = signal_cov[:,active]
                hessian = signal_cov[np.ix_(active,active)]
                weights = np.linalg.solve(hessian,signal[active])
                shifted = signal-columns@weights
                residual_cov = signal_cov-columns@np.linalg.solve(hessian,columns.T)
                penalty = signal[active]@weights
            else:
                shifted,residual_cov,penalty = signal,signal_cov,0.
            covariance = self.covariance+nu**2*residual_cov
            deviance,mean,score = self._poisson_profile(self.b+nu*shifted,np.linalg.cholesky(covariance))
            fitted_signal = shifted-nu*(residual_cov@score)
            if active:
                dual = np.linalg.solve(hessian,nu*(columns.T@score))-weights
                if min(dual)<-1e-8:
                    active.pop(int(np.argmin(dual)))
                    continue
                assert np.max(np.abs(fitted_signal[active]))<1e-7
            if min(fitted_signal)<-1e-8:
                index = int(np.argmin(fitted_signal))
                if index in active:
                    raise RuntimeError("Signal yield at active bound failed closure")
                active.append(index)
                continue
            slope = 2*score@fitted_signal
            return Profile(float(deviance+penalty),mean,float(slope),len(active))
        raise RuntimeError("Nonnegative signal profile did not converge")

    def best(self, signal, signal_cov, scale):
        def at(nu):
            return self.profile(nu,signal,signal_cov)

        if at(0).slope>=0:
            return 0.,at(0).deviance
        lo,hi = 0.,scale
        while at(hi).slope<0:
            hi *= 2
            if hi>64*scale:
                raise RuntimeError("Positive signal-strength optimum not bracketed")
        for _ in range(27):
            mid = (lo+hi)/2
            if at(mid).slope<0:
                lo = mid
            else:
                hi = mid
        best = (lo+hi)/2
        result = at(best)
        assert abs(result.slope*scale)<1e-5 and result.deviance<=at(0).deviance+1e-9
        return best,result.deviance

    def statistics(self, nu, signal, signal_cov, best, asimov):
        fit_nu,dmin = best
        obs = max(0.,self.profile(nu,signal,signal_cov).deviance-dmin) if nu>=fit_nu else 0.
        a = asimov.q(nu,signal,signal_cov)
        return obs,a,cls(obs,a)

    def upper(self, signal, signal_cov, expected, asimov):
        best = self.best(signal,signal_cov,expected)

        def at(nu):
            return self.statistics(nu,signal,signal_cov,best,asimov)

        lo,hi = best[0],max(expected,2*best[0])
        while at(hi)[2]>.05:
            hi *= 2
            if hi>64*expected:
                raise RuntimeError("Observed CLs crossing not bracketed")
        for _ in range(28):
            mid = (lo+hi)/2
            if at(mid)[2]>.05:
                lo = mid
            else:
                hi = mid
        limit = (lo+hi)/2
        qobs,qa,value = at(limit)
        assert abs(value-.05)<5e-8
        # Check the likelihood minimum and CLs crossing across the full range.
        checkpoints = np.linspace(0.,1.75*limit,13)
        assert all(self.profile(v,signal,signal_cov).deviance>=best[1]-1e-7 for v in checkpoints)
        assert np.all(np.diff([at(v)[2] for v in checkpoints])<=1e-7)
        return limit,best[0],qobs,qa


def cls(qobs,qa):
    if qa <= 0:
        assert qobs < 1e-12
        return 1.
    a = sqrt(qa)
    z = sqrt(qobs) if qobs<=qa else (qobs+qa)/(2*a)
    return erfc(z/sqrt(2))/erfc((z-a)/sqrt(2))
