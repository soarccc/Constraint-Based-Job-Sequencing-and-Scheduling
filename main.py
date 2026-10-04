# Name: Sara Abu Rub 1241214
# Partner: Sema Beidas 1241428

import sys
import re
import os
from datetime import datetime
class Job:
    def __init__(self,job_id,deadline,profit,duration,penalty,depends_on,category,cost):
        self.job_id=job_id
        self.deadline=deadline
        self.profit=profit
        self.duration=duration
        self.penalty=penalty
        self.depends_on=depends_on
        self.category=category
        self.cost=cost
        self.net_value=penalty+profit
        # net_value is used for greedy priority sorting


    def __str__(self):
        return  f"Job: {self.job_id} | Deadline: {self.deadline} | Proft: {self.profit} | Duration: {self.duration} | Penalty: {self.penalty} | Dependency: {self.depends_on} | Category: {self.category} | Cost: {self.cost} | NetValue: {self.net_value}"

class Parser:
    def __init__(self, filename):
        self.filename=filename
        self.jobs=[]

    def parse(self):
        """reads the input file, validates each line, and returns a list of job objects."""
        file=open(self.filename,"r")
        lines=file.readlines()
        file.close()

        for line in lines:
            if re.match(r"^\s*$",line) or re.match(r"^#",line):
                # Skip blank lines and comments
                continue
            line=line.strip()
            parts=line.split()
            # remove whitespace and split into fields
            if len(parts)!=8:
                continue
            if self._validate_line(parts):
                # only create Job if validation is true
              #to not crash my partner's code, turn - into none
              depends_on=None if parts[5]=="-" else parts [5]
              job=Job(parts[0],int(parts[1]),int(parts[2]),int(parts[3]),int(parts[4]),depends_on,parts[6],int(parts[7]))
              self.jobs.append(job)

        return self.jobs


    def _validate_line(self,fields):
        if not (fields[1].isdigit() and fields[2].isdigit() and fields[3].isdigit() and fields[4].isdigit() and fields[7].isdigit()):
             #check that all numeric fields are not negative
            return False
        if int(fields[3]) > int(fields[1]):
            # reject jobs where duration exceeds deadline
            return False
        if not fields[6].isalpha():
            # category must be alphabetic only
            return False
        if not re.match(r"^J\d+$",fields[0]):
            return False
        else:
            return True
    def _check_duplicates(self,jobs):
        seen=[]
        # track seen job IDs to detect duplicates
        for job in jobs:
            if job.job_id in seen:
                print(f"There is a duplicate {job.job_id}")

                return True
            else:
                seen.append(job.job_id)
        return False


    def _check_dependencies(self,jobs):
        valid_id=[]
         #get all valid job ids with no dupes
        for job in jobs:
            if job.job_id not in valid_id:
                valid_id.append(job.job_id)
            else:
                continue


        for job in jobs:
            if job.depends_on is not None:
                if job.depends_on not in valid_id:
                    return True
            #verify that each dependency exists
        return False

    def _detect_circular(self,jobs):
        d={}
        for job in jobs:
            d[job.job_id] = job.depends_on
          # build dependency map where : job_id -> depends_on
        for job in jobs:
            seen=[]
            #Reset visited list for each starting job
            # because we track for one job
            current=job.job_id 
            # its now the key for job.depends_on
            while current is not None:
                if current in seen:
                    #For each job, follow the chain and detect if we revisit a something
                    print(f"Error: circular dependency detected involving {current}")
                    return True
                seen.append(current)
                if current not in d:
                    break
                current=d[current]
                
        return False
class Scheduler:
    def __init__(self, jobs, max_budget):
        self.jobs = jobs
        self.max_budget = max_budget
        self.total_slots = max(j.deadline for j in jobs)
        self.timeline = [None] * (self.total_slots +1)
        self.scheduled = {}
        self.skipped = []
        self.budget_used = 0
    
    def sort_jobs(self):
        # First sort by net value (greedy priority)
        def get_key(j):
            return (-j.net_value, j.deadline, j.duration, j.cost)
        self.jobs.sort(key = get_key)
        # Then do a topological sort so dependencies come before dependents
        self.jobs = self.topological_sort(self.jobs)

    def topological_sort(self, jobs):
        job_map = {j.job_id : j for j in jobs}
        visited = set()
        result = []
        #skips visited jobs else it adds the new ones
        def visit(job):
            if job.job_id in visited:
                return
            visited.add(job.job_id)

            # Visit jobs with dependency
            if job.depends_on and job.depends_on in job_map:
                visit(job_map[job.depends_on])
            result.append(job)

            # Visit the rest of the jobs
        for job in jobs:
            visit(job)
            
        return result

    def find_latest_slot(self, job):
        # start from the latest possible position (right before the deadline)
        end   = job.deadline
        start = end - job.duration + 1

        # keep shifting the block one slot to the left until we find a free spot
        while start >= 1:
            # check if all slots in this block are empty
            slots_free = all(self.timeline[s] is None for s in range(start, end + 1))

            # if slots are free and category constraint is satisfied, use this block
            if slots_free and self.check_category(job, start, end):
                return start, end

            # shift the block one slot to the left and try again
            end   -= 1
            start -= 1

        # no valid slot found
        return None, None

    def check_category(self, job, start, end):
    # Check the slot just before the block
        if start > 1 and self.timeline[start - 1] is not None:
            neighbor_id = self.timeline[start - 1]
            neighbor = next(j for j in self.jobs if j.job_id == neighbor_id)
            if neighbor.category == job.category:
                return False

        # Check the slot just after the block
        if end < self.total_slots and self.timeline[end + 1] is not None:
            neighbor_id = self.timeline[end + 1]
            neighbor = next(j for j in self.jobs if j.job_id == neighbor_id)
            if neighbor.category == job.category:
                return False

        return True

    def dependency_satisfied(self, job):
        if job.depends_on is None:
            return True
        if job.depends_on not in self.scheduled:
            return False
        # Dependency must have fully completed before this job starts
        return True


    def get_dep_end(self, job):
        if job.depends_on is None:
            return 0
        start_slot, dep_end = self.scheduled[job.depends_on]
        return dep_end

    def run(self):
        self.sort_jobs()

        for job in self.jobs:
            skip_reason = None

            # check if the job this one depends on was scheduled successfully
            if job.depends_on and job.depends_on not in self.scheduled:
                skip_reason = "dependency '" + job.depends_on + "' not scheduled"

            # check if we have enough budget left for this job
            if skip_reason is None and self.budget_used + job.cost > self.max_budget:
                skip_reason = "budget exceeded"

            if skip_reason is None:
                # if there's a dependency, the job must start after it finishes
                dep_end = 0
                if job.depends_on:
                    start_slot, dep_end = self.scheduled[job.depends_on]

                # try to find a valid slot for this job
                start, end = self.find_latest_slot_after(job, dep_end)

                if start is None:
                    skip_reason = "no valid time slot found"
                else:
                    # assign the job to the timeline and track it
                    for s in range(start, end + 1):
                        self.timeline[s] = job.job_id
                    self.scheduled[job.job_id] = (start, end)
                    self.budget_used += job.cost

            # if any check failed, add to skipped list
            if skip_reason:
                self.skipped.append((job, skip_reason))
 

    def find_latest_slot_after(self, job, dep_end):
        # Job must start after dep_end, and end by deadline
        earliest_start = dep_end + 1
        end = job.deadline
        start = end - job.duration + 1
 
        while start >= earliest_start:
            slots_free = all(self.timeline[s] is None for s in range(start, end + 1))
 
            if slots_free and self.check_category(job, start, end):
                return start, end
 
            end -= 1
            start -= 1
 
        return None, None
# ----------------------------
# OUTPUT
# ----------------------------

def build_report(scheduler, jobs, input_filename, max_budget):
    job_map = {j.job_id: j for j in jobs}
 
    total_profit  = sum(job_map[jid].profit for jid in scheduler.scheduled)
    total_penalty = sum(j.penalty for j, _ in scheduler.skipped)
    net_profit    = total_profit - total_penalty
 
    lines = []
 
    lines.append("=" * 60)
    lines.append("\t\tJOB SCHEDULING REPORT")
    lines.append("=" * 60)
    lines.append(f"Timestamp  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Input File : {input_filename}")
    lines.append(f"Max Budget : {max_budget}")
    lines.append("")
 
    # Final schedule sorted by start slot
    lines.append("SCHEDULED JOBS (by time slot):")
    lines.append("-" * 60)
 
    sorted_scheduled = sorted(scheduler.scheduled.items(), key=lambda x: x[1][0])
 
    if sorted_scheduled:
        header = f"{'Job':<6} {'Slots':<10} {'Dur':<5} {'Profit':<8} {'Penalty':<9} {'Cat':<5} {'Cost':<6} {'Depends'}"
        lines.append(header)
        lines.append("-" * 60)
        for jid, (start, end) in sorted_scheduled:
            j = job_map[jid]
            dep = j.depends_on if j.depends_on else "-"
            slot_str = f"{start}-{end}"
            lines.append(f"{jid:<6} {slot_str:<10} {j.duration:<5} {j.profit:<8} {j.penalty:<9} {j.category:<5} {j.cost:<6} {dep}")
    else:
        lines.append("No jobs were scheduled.")
 
    lines.append("")
    lines.append("SKIPPED JOBS:")
    lines.append("-" * 60)
 
    if scheduler.skipped:
        for j, reason in scheduler.skipped:
            lines.append(f"  {j.job_id:<6}  Reason: {reason}  (penalty: {j.penalty})")
    else:
        lines.append("  None")
 
    lines.append("")
    lines.append("SUMMARY:")
    lines.append("-" * 60)
    lines.append(f"  Jobs Scheduled : {len(scheduler.scheduled)}")
    lines.append(f"  Jobs Skipped   : {len(scheduler.skipped)}")
    lines.append(f"  Total Profit   : {total_profit}")
    lines.append(f"  Total Penalties: {total_penalty}")
    lines.append(f"  Net Profit     : {net_profit}")
    lines.append(f"  Budget Used    : {scheduler.budget_used} / {max_budget}")
    lines.append(f"  Remaining Budg : {max_budget - scheduler.budget_used}")
    lines.append("=" * 60)
 
    return "\n".join(lines), net_profit
 
 
def print_and_save(report, output_path):
    print(report)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {output_path}")
 # validate input before scheduling
if(len(sys.argv)!=3):
    print(f"Usage: python3 main.py <jobs.txt>")
    sys.exit()

filename=sys.argv[1]

try:
    max_budget = int(sys.argv[2])
except ValueError:
    print("Error: budget must be a valid integer")
    sys.exit()
try:
    par=Parser(filename)
except FileNotFoundError:
    print("Error, file not found")
    sys.exit()
jobs=par.parse()
if not jobs:
    #if file is empty
    print("No valid jobs found in input file.")
    sys.exit()
if par._check_duplicates(jobs):
    print("Error!Duplicate jobs")
    sys.exit()
if par._check_dependencies(jobs):
    print("Job dependent on doesn't exist")
    sys.exit()
if par._detect_circular(jobs):
    print("Error! Circular dependency")
    sys.exit()

scheduler = Scheduler(jobs, max_budget)
scheduler.run()

report, net_profit = build_report(scheduler, jobs, filename, max_budget)
print_and_save(report, "output/result.txt")
