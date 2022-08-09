use std::{collections::HashSet, fmt::Debug, fs, rc::Rc};

struct Map {
    caves: HashSet<Rc<Cave>>,
    connections: HashSet<Connection>,
}

#[derive(Hash, PartialEq, Eq)]
struct Cave {
    name: String,
    c_type: CaveType,
}

#[derive(Hash, PartialEq, Eq)]
struct Connection {
    c1: Rc<Cave>,
    c2: Rc<Cave>,
}

#[derive(Hash, PartialEq, Eq, Debug)]
enum CaveType {
    Start,
    End,
    Large,
    Small,
}

impl Debug for Cave {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.name.to_string())
    }
}

impl Connection {
    fn new(c1: Rc<Cave>, c2: Rc<Cave>) -> Self {
        Self { c1, c2 }
    }

    fn get_neighbour(&self, cave: &Rc<Cave>) -> Option<Rc<Cave>> {
        if *cave == self.c1 {
            Some(self.c2.clone())
        } else if *cave == self.c2 {
            Some(self.c1.clone())
        } else {
            None
        }
    }
}

impl Map {
    fn new(filename: &str) -> Self {
        let vec: Vec<(Cave, Cave)> = fs::read_to_string(filename)
            .unwrap()
            .split_whitespace()
            .map(|line| {
                let pos = line.find('-').unwrap();
                let c1 = Cave::new(line[..pos].to_string());
                let c2 = Cave::new(line[pos + 1..].to_string());
                (c1, c2)
            })
            .collect();

        let mut caves = HashSet::new();
        let mut connections = HashSet::new();
        for (c1, c2) in vec {
            let rc1 = Rc::new(c1);
            let rc2 = Rc::new(c2);
            connections.insert(Connection::new(rc1.clone(), rc2.clone()));
            caves.insert(rc1);
            caves.insert(rc2);
        }
        Self { caves, connections }
    }

    fn print(&self) {
        println!("caves");
        for c in self.caves.iter() {
            println!(" {}: {:#?}", c.name, c.c_type);
        }

        println!("connections");
        for c in self.connections.iter() {
            println!(" {}-{}", c.c1.name, c.c2.name);
        }
    }
}

struct Solver {
    map: Map,
    routes: Vec<Vec<Rc<Cave>>>,
}

impl Solver {
    fn new(map: Map) -> Self {
        let routes = vec![];
        Self { map, routes }
    }

    fn solve(&self) -> usize {
        let current_cave = self.get_start();
        let mut route = vec![current_cave.clone()];
        self.solve_recursively(&mut route, current_cave);
        println!("{:#?}", route);
        0
    }

    fn solve_recursively(
        &self,
        route: &mut Vec<Rc<Cave>>,
        most_recent: Rc<Cave>,
    ) -> std::result::Result<(), ()> {
        for n in self.get_neighbours_of(&most_recent).iter() {
            println!("{}", n.name);
            if Self::adding_cave_to_route_would_be_valid(route, n) {
                route.push(n.clone());
                if n.c_type == CaveType::End {
                    return Ok(());
                }
                self.solve_recursively(route, n.clone());
            }
        }
        Err(())
    }

    fn adding_cave_to_route_would_be_valid(route: &[Rc<Cave>], cave: &Rc<Cave>) -> bool {
        if cave.c_type == CaveType::Start || route.iter().any(|c| c.c_type == CaveType::End) {
            false
        } else {
            !(cave.c_type == CaveType::Small && route.contains(cave))
        }
    }

    fn get_neighbours_of(&self, cave: &Rc<Cave>) -> Vec<Rc<Cave>> {
        self.map
            .connections
            .iter()
            .filter_map(|c| c.get_neighbour(cave))
            .collect()
    }

    fn get_start(&self) -> Rc<Cave> {
        for c in self.map.caves.iter() {
            if c.c_type == CaveType::Start {
                return c.clone();
            }
        }
        panic!("Map did not contain a start cave")
    }
}
impl CaveType {
    fn from_str(name: &str) -> Self {
        if name == "start" {
            CaveType::Start
        } else if name == "end" {
            CaveType::End
        } else if name.chars().next().unwrap().is_uppercase() {
            CaveType::Large
        } else {
            CaveType::Small
        }
    }
}

impl Cave {
    fn new(name: String) -> Self {
        let c_type = CaveType::from_str(&name);
        Self { name, c_type }
    }
}
fn main() {
    let map = Map::new("example.txt");
    map.print();
    let solver = Solver::new(map);
    println!("{}", solver.solve());
}
