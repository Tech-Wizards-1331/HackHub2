from participant.models import Team

def get_teams_for_allocation(hackathon_id):
    teams_qs = Team.objects.filter(hackathon_id=hackathon_id).prefetch_related('members', 'leader')
    final_teams = []
    
    for team in teams_qs:
        members = []
        if team.leader:
            members.append(team.leader.email)
        for m in team.members.all():
            members.append(m.name or m.email)
            
        if members:
            final_teams.append({
                "name": team.name,
                "members": members
            })
            
    return final_teams

def build_bench_list(rooms_config):
    """Expand room configs into a flat ordered list of bench slots."""
    benches = []
    for room in rooms_config:
        room_no = room["room_no"]
        room_type = room.get("type", "configured")

        if room_type == "open":
            # Auditorium / library — individual seats, no bench rows
            total_seats = int(room.get("total_seats", 0))
            seats_per_row = max(1, int(room.get("seats_per_row", 20)))
            row_number = 1
            for i in range(1, total_seats + 1):
                col = ((i - 1) % seats_per_row) + 1
                if i > 1 and col == 1:
                    row_number += 1
                benches.append({
                    "room": room_no,
                    "room_type": "open",
                    "section": "Open Seating",
                    "row": f"R{row_number}",
                    "row_number": row_number,
                    "bench": col,
                    "seat_number": i,
                    "capacity": 1,
                    "assigned": [],
                })
        else:
            col_num = 1
            for col in room.get("columns", []):
                bench_count = int(col.get("bench_count", 1))
                capacity = int(col.get("capacity", 1))
                for bench_pos in range(1, bench_count + 1):
                    benches.append({
                        "room": room_no,
                        "room_type": "configured",
                        "section": room_no,
                        "row": f"R{bench_pos}",
                        "row_number": bench_pos,
                        "bench": col_num,
                        "capacity": capacity,
                        "assigned": [],
                    })
                col_num += 1

    return benches

def allocate(teams, rooms_config):
    benches = build_bench_list(rooms_config)
    total_capacity = sum(b["capacity"] for b in benches)
    total_members = sum(len(t["members"]) for t in teams)

    # Pools track remaining members per team (sorted largest first)
    pools = sorted(
        [{"name": t["name"], "members": list(t["members"]), "idx": 0} for t in teams],
        key=lambda p: len(p["members"]),
        reverse=True,
    )

    def _remaining(p):
        return len(p["members"]) - p["idx"]

    # Group benches by room
    room_to_benches = {}
    for b in benches:
        if b["room"] not in room_to_benches:
            room_to_benches[b["room"]] = []
        room_to_benches[b["room"]].append(b)

    # Ensure benches are ordered by row then bench
    for r in room_to_benches:
        room_to_benches[r].sort(key=lambda b: (b["row_number"], b["bench"]))

    # Pre-calculate room capacities
    room_free_space = {
        r: sum(b["capacity"] for b in bs) 
        for r, bs in room_to_benches.items()
    }

    seat_lists = {p["name"]: [] for p in pools}

    for pool in pools:
        rem = _remaining(pool)
        if rem <= 0: continue
        
        # 1. Layout-Aware Room Selection (Strict "Same Team, Same Room")
        best_room_score = -1
        target_room = None
        
        for r_no, r_benches in room_to_benches.items():
            if room_free_space[r_no] < rem: continue
            
            # Calculate Max Contiguous Empty Block in this room
            max_block = 0
            rows = {}
            for b in r_benches:
                rn = b["row_number"]
                if rn not in rows: rows[rn] = []
                rows[rn].append(b)
            
            for rn in rows:
                row_bs = sorted(rows[rn], key=lambda x: x["bench"])
                cur_b = 0
                last_c = -1
                for b in row_bs:
                    # For scoring, we specifically look for EMPTY contiguous blocks
                    if not b["assigned"]:
                        if last_c == -1 or b["bench"] == last_c + 1:
                            cur_b += b["capacity"]
                        else:
                            max_block = max(max_block, cur_b)
                            cur_b = b["capacity"]
                        last_c = b["bench"]
                    else:
                        max_block = max(max_block, cur_b)
                        cur_b = 0
                        last_c = -1
                max_block = max(max_block, cur_b)
            
            # Scoring Logic:
            # 1. Perfect Fit (fits in one contiguous block): Score = 10000 - room_size 
            #    (High base score, but prefer smallest room to save large rooms)
            # 2. Fragmented Fit: Score = max_block (Size of the biggest chunk we can give them)
            if max_block >= rem:
                score = 10000 - room_free_space[r_no]
            else:
                score = max_block
            
            if score > best_room_score:
                best_room_score = score
                target_room = r_no

        # Fallback: if no room fits rem, pick the room with the most total space
        if not target_room:
            if not room_free_space:
                continue
            target_room = max(room_free_space.keys(), key=lambda r: room_free_space[r])
        
        if room_free_space[target_room] <= 0:
            continue

        last_bench = None
        while _remaining(pool) > 0 and room_free_space[target_room] > 0:
            curr_rem = _remaining(pool)
            best_bench = None
            
            def is_clean(b):
                return not b["assigned"] or all(a["team"] == pool["name"] for a in b["assigned"])

            if not last_bench:
                # --- INITIAL BENCH SELECTION ---
                # 1. Priority: Single EMPTY bench that fits the entire team
                for bench in room_to_benches[target_room]:
                    free = bench["capacity"] - len(bench["assigned"])
                    if not bench["assigned"] and free >= curr_rem:
                        if not best_bench or free < (best_bench["capacity"] - len(best_bench["assigned"])):
                            best_bench = bench
                
                # 2. Priority: Any EMPTY bench (even if it doesn't fit the whole team)
                if not best_bench:
                    empty_benches = [b for b in room_to_benches[target_room] if not b["assigned"]]
                    if empty_benches:
                        best_bench = max(empty_benches, key=lambda b: b["capacity"])

                # 3. Fallback: Any bench with space (Mixed Bench Penalty applied)
                if not best_bench:
                    possible = [b for b in room_to_benches[target_room] if (b["capacity"] - len(b["assigned"])) > 0]
                    if possible:
                        best_bench = max(possible, key=lambda b: b["capacity"] - len(b["assigned"]))
            else:
                # --- SUBSEQUENT BENCH SELECTION (Strict Adjacency + Mixed Penalty) ---
                # 1. Priority: Adjacent Column (Same Row, Side-by-Side) - PREFER CLEAN
                adj_col = [
                    b for b in room_to_benches[target_room] 
                    if b["row_number"] == last_bench["row_number"] 
                    and abs(b["bench"] - last_bench["bench"]) == 1
                    and (b["capacity"] - len(b["assigned"])) > 0
                ]
                if adj_col:
                    clean_adj = [b for b in adj_col if is_clean(b)]
                    best_bench = max(clean_adj, key=lambda b: b["capacity"] - len(b["assigned"])) if clean_adj else max(adj_col, key=lambda b: b["capacity"] - len(b["assigned"]))

                # 2. Priority: Same Row (Any Column, Closest First) - PREFER CLEAN
                if not best_bench:
                    same_row = [b for b in room_to_benches[target_room] if b["row_number"] == last_bench["row_number"] and (b["capacity"] - len(b["assigned"])) > 0]
                    if same_row:
                        clean_row = [b for b in same_row if is_clean(b)]
                        candidates = clean_row if clean_row else same_row
                        best_bench = min(candidates, key=lambda b: abs(b["bench"] - last_bench["bench"]))

                # 3. Priority: Back-to-Back (Adjacent Row, Same Column) - PREFER CLEAN
                if not best_bench:
                    back_to_back = [
                        b for b in room_to_benches[target_room] 
                        if abs(b["row_number"] - last_bench["row_number"]) == 1 
                        and b["bench"] == last_bench["bench"]
                        and (b["capacity"] - len(b["assigned"])) > 0
                    ]
                    if back_to_back:
                        clean_back = [b for b in back_to_back if is_clean(b)]
                        candidates = clean_back if clean_back else back_to_back
                        best_bench = max(candidates, key=lambda b: b["capacity"] - len(b["assigned"]))

                # 4. Priority: Adjacent Row (Any Column, Closest First) - PREFER CLEAN
                if not best_bench:
                    adj_row = [b for b in room_to_benches[target_room] if abs(b["row_number"] - last_bench["row_number"]) == 1 and (b["capacity"] - len(b["assigned"])) > 0]
                    if adj_row:
                        clean_adj_row = [b for b in adj_row if is_clean(b)]
                        candidates = clean_adj_row if clean_adj_row else adj_row
                        best_bench = min(candidates, key=lambda b: abs(b["bench"] - last_bench["bench"]))

                # 5. Priority: Any CLEAN bench that fits the WHOLE remainder
                if not best_bench:
                    for bench in room_to_benches[target_room]:
                        free = bench["capacity"] - len(bench["assigned"])
                        if is_clean(bench) and free >= curr_rem:
                            if not best_bench or free < (best_bench["capacity"] - len(best_bench["assigned"])):
                                best_bench = bench

                # 6. Fallback: Any available bench in the room
                if not best_bench:
                    possible = [b for b in room_to_benches[target_room] if (b["capacity"] - len(b["assigned"])) > 0]
                    if possible:
                        clean_possible = [b for b in possible if is_clean(b)]
                        best_bench = max(clean_possible, key=lambda b: b["capacity"] - len(b["assigned"])) if clean_possible else max(possible, key=lambda b: b["capacity"] - len(b["assigned"]))

            if not best_bench: break

            take = min(curr_rem, best_bench["capacity"] - len(best_bench["assigned"]))
            chunk = pool["members"][pool["idx"]: pool["idx"] + take]
            pool["idx"] += take
            room_free_space[target_room] -= take
            last_bench = best_bench
            
            for m in chunk:
                best_bench["assigned"].append({"member": m, "team": pool["name"]})

            seat_lists[pool["name"]].append({
                "room": best_bench["room"],
                "section": best_bench["section"],
                "row": best_bench["row"],
                "bench": best_bench["bench"],
                "seats": list(range(len(best_bench["assigned"]) - take + 1, len(best_bench["assigned"]) + 1)),
                "members": chunk,
            })

    team_results = []
    for t in pools:
        seats = seat_lists[t["name"]]
        score = 0
        if seats:
            rooms = set(s["room"] for s in seats)
            rows = set(f"{s['room']}-{s['row']}" for s in seats)
            bench_ids = set(f"{s['room']}-{s['row']}-{s['bench']}" for s in seats)
            score = 100 - (len(rooms)-1)*50 - (len(rows)-1)*10 - (len(bench_ids)-1)*2
            score = max(0, score)
        
        team_results.append({
            "name": t["name"],
            "members": t["members"],
            "member_count": len(t["members"]),
            "seats": seats,
            "proximity_score": score,
            "unallocated": t["members"][t["idx"]:]
        })

    room_view = {}
    for b in benches:
        room = b["room"]
        row = b["row"]
        if room not in room_view:
            room_view[room] = {"room_type": b.get("room_type", "configured"), "rows": {}}
        if row not in room_view[room]["rows"]:
            room_view[room]["rows"][row] = { "section": b["section"], "benches": [] }
        
        bench_entry = {
            "bench": b["bench"],
            "capacity": b["capacity"],
            "assigned": b["assigned"],
            "is_full": len(b["assigned"]) >= b["capacity"],
            "is_empty": len(b["assigned"]) == 0,
        }
        if b.get("room_type") == "open":
            bench_entry["seat_number"] = b.get("seat_number")
        room_view[room]["rows"][row]["benches"].append(bench_entry)

    unallocated_total = sum(len(t["unallocated"]) for t in team_results)

    return {
        "teams": team_results,
        "room_view": room_view,
        "stats": {
            "total_teams": len(teams),
            "total_members": total_members,
            "total_capacity": total_capacity,
            "allocated": total_members - unallocated_total,
            "unallocated": unallocated_total,
            "rooms_used": len(room_view),
        }
    }
