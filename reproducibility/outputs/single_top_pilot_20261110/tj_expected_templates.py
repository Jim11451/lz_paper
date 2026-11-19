"""Approximate AH 1b 1FJ signal templates from existing tj LHE files."""

import gzip
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np


def read_events(path):
    events = []
    inside = False
    with gzip.open(path, 'rt') as file:
        for line in file:
            line = line.strip()
            if line == '<event>':
                inside = True
                top = jet = None
                invisible = np.zeros(2)
                incoming = np.zeros(4)
            elif line == '</event>':
                assert top is not None and jet is not None
                events.append(np.r_[top, jet, invisible, np.sqrt(incoming[0]**2 - incoming[3]**2)])
                inside = False
            elif inside and line and line[0] not in '<#':
                fields = line.split()
                if len(fields) != 13:
                    continue
                pdg, status = map(int, fields[:2])
                vector = np.array([float(fields[i]) for i in [9, 6, 7, 8]])
                if status == -1:
                    incoming += vector
                elif status == 1:
                    if abs(pdg) == 6:
                        top = vector
                    elif 1 <= abs(pdg) <= 4:
                        jet = vector
                    elif abs(pdg) in (100051, 100052):
                        invisible += vector[1:3]
    return np.asarray(events)


def direction(cosine, phi):
    sine = np.sqrt(1 - cosine**2)
    return np.column_stack((sine*np.cos(phi), sine*np.sin(phi), cosine))


def boost(energy, momentum, beta):
    beta2 = np.sum(beta**2, axis=1)
    gamma = 1/np.sqrt(1-beta2)
    dot = np.sum(beta*momentum, axis=1)
    factor = (gamma**2/(gamma+1))*dot + gamma*energy
    return gamma*(energy+dot), momentum + factor[:, None]*beta


def top_decay(top, rng):
    mt = np.sqrt(top[:, 0]**2 - np.sum(top[:, 1:]**2, axis=1))
    mw = 80.385
    momentum = (mt**2 - mw**2)/(2*mt)
    w_energy = mt-momentum
    axis = direction(rng.uniform(-1, 1, len(top)), rng.uniform(0, 2*np.pi, len(top)))
    # Spin-averaged top, with the SM longitudinal/transverse W helicity mix.
    cos = rng.uniform(-1, 1, len(top))
    reject = rng.random(len(top)) > 1 - (.4125/.6375)*cos**2
    while np.any(reject):
        cos[reject] = rng.uniform(-1, 1, int(reject.sum()))
        reject[reject] = rng.random(int(reject.sum())) > 1 - (.4125/.6375)*cos[reject]**2
    phi = rng.uniform(0, 2*np.pi, len(top))
    basis_x = np.cross(axis, [0, 0, 1.])
    basis_x /= np.linalg.norm(basis_x, axis=1)[:, None]
    basis_y = np.cross(axis, basis_x)
    coordinates = direction(cos, phi)
    light = .5*mw*(coordinates[:, 0, None]*basis_x + coordinates[:, 1, None]*basis_y + cos[:, None]*axis)
    w_beta = (momentum/w_energy)[:, None]*axis
    top_beta = top[:, 1:]/top[:, 0, None]
    b = boost(momentum, -momentum[:, None]*axis, top_beta)[1]
    j1 = boost(*boost(.5*mw, light, w_beta), top_beta)[1]
    j2 = boost(*boost(.5*mw, -light, w_beta), top_beta)[1]
    return np.stack((b, j1, j2), axis=1)


def delta_phi(a, b):
    return np.abs((a-b+np.pi) % (2*np.pi)-np.pi)


def histogram(met, mask, weights=None):
    return np.histogram(met[mask], bins=[*range(250, 531, 20), np.inf],
                        weights=None if weights is None else weights[mask])[0].tolist()


def analyze(item):
    index, row = item
    events = read_events(Path(row['banner']).with_name('unweighted_events.lhe.gz'))
    assert len(events) == int(row['events'])
    met = np.linalg.norm(events[:, 8:10], axis=1)
    spectator = events[:, 5:8]
    shat = events[:, 10]
    pt = np.linalg.norm(spectator[:, :2], axis=1)
    eta = np.arcsinh(spectator[:, 2]/pt)
    forward = (met > 250) & (pt > 30) & (2.4 < np.abs(eta)) & (np.abs(eta) < 4.)
    draws = 48
    selected = np.repeat(events[forward], draws, axis=0)
    met_decay = np.repeat(met[forward], draws)
    shat_decay = np.repeat(shat[forward], draws)
    rng = np.random.default_rng(60241+index)
    jets = top_decay(selected[:, :4], rng)
    all_jets = np.concatenate((jets, selected[:, None, 5:8]), axis=1)
    jet_pt = np.linalg.norm(all_jets[:, :, :2], axis=2)
    jet_eta = np.arcsinh(all_jets[:, :, 2]/jet_pt)
    jet_phi = np.arctan2(all_jets[:, :, 1], all_jets[:, :, 0])
    accept = np.all((jet_pt[:, :3] > 30) & (np.abs(jet_eta[:, :3]) < 2.4), axis=1)
    for i in range(4):
        for j in range(i):
            accept &= (jet_eta[:, i]-jet_eta[:, j])**2 + delta_phi(jet_phi[:, i], jet_phi[:, j])**2 > .4**2
    leading = np.argsort(jet_pt[:, :3], axis=1)[:, -2:]
    miss_phi = np.arctan2(selected[:, 9], selected[:, 8])
    phi = delta_phi(jet_phi, miss_phi[:, None])
    accept &= np.all(np.take_along_axis(phi[:, :3], leading, axis=1) > .8, axis=1)
    accept &= 2*jet_pt[:, 0]*met_decay*(1-np.cos(phi[:, 0])) > 140**2
    weights = np.full(len(selected), float(row['sigma_fb']) / (draws*len(events)))
    truth_weight = np.full(len(events), float(row['sigma_fb'])/len(events))
    result = {key: row[key] for key in ('benchmark','mv_GeV','mchi_GeV','gt','gchi','sigma_fb')}
    for ceiling in (750, 1000, 1500, float('inf')):
        label = 'full' if np.isinf(ceiling) else str(ceiling)
        result['fiducial_'+label] = histogram(met_decay, accept & (shat_decay < ceiling), weights)
        result['forward_'+label] = histogram(met, forward & (shat < ceiling), truth_weight)
    return result


with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(analyze, enumerate(samples)):
        print(json.dumps(result), flush=True)
