namespace Sistema_de_Gestão_Hospitalar
{
    public class Program
    {
        static List<Paciente> pacientes = new List<Paciente>();
        static List<Medico> medicos = new List<Medico>();
        static List<Enfermeiro> enfermeiros = new List<Enfermeiro>();
        static List<Consulta> consultas = new List<Consulta>();

        static void Main(string[] args)
        {
            bool sair = false;

            while (!sair)
            {
                Console.Clear();
                Console.WriteLine("=== Sistema de Gestão Hospitalar ===");
                Console.WriteLine("1. Adicionar Paciente");
                Console.WriteLine("2. Adicionar Médico");
                Console.WriteLine("3. Adicionar Enfermeiro");
                Console.WriteLine("4. Agendar Consulta");
                Console.WriteLine("5. Listar Pacientes");
                Console.WriteLine("6. Listar Médicos");
                Console.WriteLine("7. Listar Consultas");
                Console.WriteLine("0. Sair");
                Console.Write("Escolha uma opção: ");
                string opcao = Console.ReadLine();

                switch (opcao)
                {
                    case "1":
                        AdicionarPaciente();
                        break;
                    case "2":
                        AdicionarMedico();
                        break;
                    case "3":
                        AdicionarEnfermeiro();
                        break;
                    case "4":
                        AgendarConsulta();
                        break;
                    case "5":
                        ListarPacientes();
                        break;
                    case "6":
                        ListarMedicos();
                        break;
                    case "7":
                        ListarConsultas();
                        break;
                    case "0":
                        sair = true;
                        break;
                    default:
                        Console.WriteLine("Opção inválida!");
                        break;
                }

                if (!sair)
                {
                    Console.WriteLine("\nPressione Enter para continuar...");
                    Console.ReadLine();
                }
            }
        }

        static void AdicionarPaciente()
        {
            Console.WriteLine("=== Adicionar Paciente ===");
            Paciente p = new Paciente();

            Console.Write("Nome: ");
            p.Nome = Console.ReadLine();

            Console.Write("Número do Processo: ");
            p.NumProcesso = Console.ReadLine();

            Console.Write("Grupo Sanguíneo: ");
            p.GrupoSanguineo = Console.ReadLine();

            pacientes.Add(p);
            Console.WriteLine("Paciente adicionado com sucesso!");
        }

        static void AdicionarMedico()
        {
            Console.WriteLine("=== Adicionar Médico ===");
            Medico m = new Medico();

            Console.Write("Nome: ");
            m.Nome = Console.ReadLine();

            Console.Write("Especialidade: ");
            m.Especialidade = Console.ReadLine();

            medicos.Add(m);
            Console.WriteLine("Médico adicionado com sucesso!");
        }

        static void AdicionarEnfermeiro()
        {
            Console.WriteLine("=== Adicionar Enfermeiro ===");
            Enfermeiro e = new Enfermeiro();

            Console.Write("Nome: ");
            e.Nome = Console.ReadLine();

            Console.WriteLine("Turno (MANHA, TARDE, NOITE): ");
            if (Enum.TryParse(Console.ReadLine(), out TipoTurno turno))
                e.Turno = turno;

            enfermeiros.Add(e);
            Console.WriteLine("Enfermeiro adicionado com sucesso!");
        }

        static void AgendarConsulta()
        {
            Console.WriteLine("=== Agendar Consulta ===");

            if (pacientes.Count == 0 || medicos.Count == 0)
            {
                Console.WriteLine("Não há pacientes ou médicos cadastrados!");
                return;
            }

            Console.WriteLine("Escolha Paciente:");
            for (int i = 0; i < pacientes.Count; i++)
                Console.WriteLine($"{i + 1}. {pacientes[i].Nome}");
            int pIndex = int.Parse(Console.ReadLine()) - 1;

            Console.WriteLine("Escolha Médico:");
            for (int i = 0; i < medicos.Count; i++)
                Console.WriteLine($"{i + 1}. {medicos[i].Nome}");
            int mIndex = int.Parse(Console.ReadLine()) - 1;

            Consulta c = new Consulta();
            c.Paciente = pacientes[pIndex];
            c.Medico = medicos[mIndex];
            c.Data = DateTime.Now;

            consultas.Add(c);
            Console.WriteLine("Consulta agendada com sucesso!");
        }

        static void ListarPacientes()
        {
            Console.WriteLine("=== Lista de Pacientes ===");
            foreach (var p in pacientes)
                Console.WriteLine($"Nome: {p.Nome}, Processo: {p.NumProcesso}, Grupo Sanguíneo: {p.GrupoSanguineo}");
        }

        static void ListarMedicos()
        {
            Console.WriteLine("=== Lista de Médicos ===");
            foreach (var m in medicos)
                Console.WriteLine($"Nome: {m.Nome}, Especialidade: {m.Especialidade}");
        }

        static void ListarConsultas()
        {
            Console.WriteLine("=== Lista de Consultas ===");
            foreach (var c in consultas)
                Console.WriteLine($"Paciente: {c.Paciente.Nome}, Médico: {c.Medico.Nome}, Data: {c.Data}");
        }
    }
}
