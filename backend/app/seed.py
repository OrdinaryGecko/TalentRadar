from app.repository import load_candidate_fixture


def main() -> None:
    candidates = load_candidate_fixture()

    print(f"loaded {len(candidates)} candidate profiles")

    for candidate in candidates:
        print(
            f"- {candidate.id}: {candidate.full_name} | "
            f"{candidate.current_title} | {candidate.persona.value}"
        )


if __name__ == "__main__":
    main()
