#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Le ratio de synthese change-t-il avec la longueur du texte ? Mesure sur les DEUX moteurs.

Pourquoi ce script existe. Mon article Kokoro affirme x0,75 sur un texte long, et precise
lui-meme que c'etait « une mesure unique, non repetee ». Mon article Piper dit noir sur blanc :
« Je n'ai pas refait ce test long avec Piper : je ne sais donc pas si Piper se degrade aussi,
ni dans quelle proportion. » Deux lacunes que j'ai publiees ; celui-ci les comble.

Les deux textes sont REPRODUITS a l'identique, jamais recopies :
  - court : les 8 phrases de outils/mesure_tts.py (505 caracteres), le texte de reference
  - long  : les 12 phrases du script de mon episode 0 (media/episodes/jour-000.json,
            950 caracteres), c'est-a-dire EXACTEMENT le texte sur lequel le x0,75 de Kokoro
            avait ete mesure. Sans ca, la comparaison ne vaudrait rien.

Les quatre combinaisons tournent dans la MEME session, en serie, sur une machine a deux coeurs :
le but est de comparer court contre long sans qu'un changement d'etat machine explique l'ecart.
"""
import json, sys, time, resource, subprocess, tempfile, os, statistics
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from mesure_tts import PHRASES as COURT, MODELE as KOKORO_MODELE, VOIX_BIN as KOKORO_VOIX

MODELES_PIPER = RACINE / "outils" / "modeles" / "piper"
VOIX_PIPER = "fr_FR-siwis-medium"
EPISODE = RACINE / "media" / "episodes" / "jour-000.json"
SORTIE = RACINE / "media" / "mesures"


def texte_long():
    d = json.load(open(EPISODE, encoding="utf-8"))
    phrases = [p["texte"] for p in d["plans"] if p.get("texte")]
    return phrases


def cpu_total():
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


def duree_ffprobe(chemin):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", chemin],
                       capture_output=True, text=True, timeout=60)
    return float(r.stdout.strip())


def ecrire_wav(chemin, echantillons, sr):
    import wave
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(echantillons.tobytes())


def mesure_piper(phrases, passes, etiquette):
    from piper import PiperVoice
    t0 = time.perf_counter()
    voix = PiperVoice.load(str(MODELES_PIPER / (VOIX_PIPER + ".onnx")),
                           str(MODELES_PIPER / (VOIX_PIPER + ".onnx.json")))
    chargement = time.perf_counter() - t0
    sr = voix.config.sample_rate
    lignes = []
    for n in range(1, passes + 1):
        morceaux, ech = [], 0
        c0, t0 = cpu_total(), time.perf_counter()
        for ph in phrases:
            for ch in voix.synthesize(ph):
                a = np.frombuffer(ch.audio_int16_bytes, dtype=np.int16)
                morceaux.append(a); ech += len(a)
        calc = time.perf_counter() - t0
        cpu = (cpu_total() - c0) / calc * 100.0
        audio = ech / sr
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            nom = f.name
        ecrire_wav(nom, np.concatenate(morceaux), sr)
        verif = duree_ffprobe(nom)
        os.unlink(nom)
        lignes.append({"passe": n, "audio_s": audio, "audio_ffprobe_s": verif,
                       "calcul_s": calc, "ratio": audio / calc, "cpu_pct": cpu})
        print("  piper  %-6s passe %d : audio %6.2f s  calcul %6.2f s  ratio x%.2f  cpu %3.0f %%"
              % (etiquette, n, audio, calc, audio / calc, cpu))
    return {"moteur": "piper-" + VOIX_PIPER, "chargement_s": chargement, "passes": lignes}


def mesure_kokoro(phrases, passes, etiquette):
    from kokoro_onnx import Kokoro
    t0 = time.perf_counter()
    k = Kokoro(str(KOKORO_MODELE), str(KOKORO_VOIX))
    chargement = time.perf_counter() - t0
    lignes = []
    for n in range(1, passes + 1):
        audio = 0.0
        c0, t0 = cpu_total(), time.perf_counter()
        for ph in phrases:
            s, sr = k.create(ph, voice="ff_siwis", speed=1.0, lang="fr-fr")
            audio += len(np.asarray(s)) / sr
        calc = time.perf_counter() - t0
        cpu = (cpu_total() - c0) / calc * 100.0
        lignes.append({"passe": n, "audio_s": audio, "calcul_s": calc,
                       "ratio": audio / calc, "cpu_pct": cpu})
        print("  kokoro %-6s passe %d : audio %6.2f s  calcul %6.2f s  ratio x%.2f  cpu %3.0f %%"
              % (etiquette, n, audio, calc, audio / calc, cpu))
    return {"moteur": "kokoro-82m ff_siwis", "chargement_s": chargement, "passes": lignes}


def main():
    passes_piper = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    passes_kokoro = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    long_ = texte_long()
    print("texte court : %d caracteres, %d phrases" % (sum(map(len, COURT)), len(COURT)))
    print("texte long  : %d caracteres, %d phrases (script de l'episode 0)"
          % (sum(map(len, long_)), len(long_)))
    print()
    r = {
        "date_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "machine": os.uname().machine, "noyau": os.uname().release,
        "textes": {"court": {"caracteres": sum(map(len, COURT)), "phrases": len(COURT),
                             "source": "outils/mesure_tts.py (importe)"},
                   "long": {"caracteres": sum(map(len, long_)), "phrases": len(long_),
                            "source": "media/episodes/jour-000.json (importe)"}},
        "mesures": {},
    }
    r["mesures"]["piper_court"] = mesure_piper(COURT, passes_piper, "court")
    r["mesures"]["piper_long"] = mesure_piper(long_, passes_piper, "long")
    r["mesures"]["kokoro_court"] = mesure_kokoro(COURT, passes_kokoro, "court")
    r["mesures"]["kokoro_long"] = mesure_kokoro(long_, passes_kokoro, "long")

    SORTIE.mkdir(parents=True, exist_ok=True)
    nom = SORTIE / ("longueur-%s.json" % time.strftime("%Y%m%d-%H%M", time.gmtime()))
    json.dump(r, open(nom, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print()
    for cle, m in r["mesures"].items():
        ratios = [p["ratio"] for p in m["passes"]]
        print("%-14s ratio x%.2f a x%.2f (mediane x%.2f) sur %d passes"
              % (cle, min(ratios), max(ratios), statistics.median(ratios), len(ratios)))
    print("\ndonnees brutes :", nom)
    return 0


if __name__ == "__main__":
    sys.exit(main())
