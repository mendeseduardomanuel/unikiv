using Sistema_de_Gestão_Escolar_Simples.Model;

namespace Sistema_de_Gestão_Escolar_Simples
{
   /* Sistema de Gestão Escolar Simples
Contexto: Uma escola precisa de gerir informações sobre alunos e professores.*/
    public class Program
    {
        static List<Aluno> alunos = new List<Aluno>();
        static List<Professor> professores = new List<Professor>();
        static List<Turma> turmas = new List<Turma>();

        static void Main(string[] args)
        {
            int opcao;

            do
            {
                Console.Clear();
                Console.WriteLine("=== SISTEMA ESCOLAR ===");
                Console.WriteLine("1. Criar Professor");
                Console.WriteLine("2. Criar Aluno");
                Console.WriteLine("3. Criar Turma");
                Console.WriteLine("4. Adicionar Aluno à Turma");
                Console.WriteLine("5. Lançar Nota");
                Console.WriteLine("6. Listar Alunos");
                Console.WriteLine("0. Sair");
                Console.Write("Escolha: ");

                opcao = int.Parse(Console.ReadLine());

                switch (opcao)
                {
                    case 1: CriarProfessor(); break;
                    case 2: CriarAluno(); break;
                    case 3: CriarTurma(); break;
                    case 4: AdicionarAlunoTurma(); break;
                    case 5: LancarNota(); break;
                    case 6: ListarAlunos(); break;
                }

                Console.WriteLine("\nPressione ENTER...");
                Console.ReadLine();

            } while (opcao != 0);
        }

        static void CriarProfessor()
        {
            Console.Write("Nome: ");
            string nome = Console.ReadLine();

            Console.Write("Telefone: ");
            string telefone = Console.ReadLine();

            Console.Write("Especialidade: ");
            string esp = Console.ReadLine();

            Console.Write("Departamento: ");
            string dep = Console.ReadLine();

            Console.Write("Salário: ");
            double salario = double.Parse(Console.ReadLine());

            Professor prof = new Professor(nome, DateTime.Now, telefone, esp, dep, salario);
            professores.Add(prof);

            Console.WriteLine("Professor criado!");
        }

        static void CriarAluno()
        {
            Console.Write("Nome: ");
            string nome = Console.ReadLine();

            Console.Write("Telefone: ");
            string telefone = Console.ReadLine();

            Console.Write("Número: ");
            int numero = int.Parse(Console.ReadLine());

            Console.Write("Curso: ");
            string curso = Console.ReadLine();

            Aluno aluno = new Aluno(nome, DateTime.Now, telefone, numero, curso);
            alunos.Add(aluno);

            Console.WriteLine("Aluno criado!");
        }

        static void CriarTurma()
        {
            Console.Write("Código: ");
            string codigo = Console.ReadLine();

            Console.Write("Ano: ");
            int ano = int.Parse(Console.ReadLine());

            Console.Write("Capacidade: ");
            int cap = int.Parse(Console.ReadLine());

            Turma turma = new Turma(codigo, ano, cap);

            // escolher professor
            if (professores.Count == 0)
            {
                Console.WriteLine("Nenhum professor disponível!");
                return;
            }

            Console.WriteLine("Escolha um professor:");
            for (int i = 0; i < professores.Count; i++)
            {
                Console.WriteLine($"{i} - {professores[i].GetNome()}");
            }

            int escolha = int.Parse(Console.ReadLine());
            turma.Professor = professores[escolha];

            turmas.Add(turma);

            Console.WriteLine("Turma criada!");
        }

        static void AdicionarAlunoTurma()
        {
            if (turmas.Count == 0 || alunos.Count == 0)
            {
                Console.WriteLine("Sem dados suficientes!");
                return;
            }

            Console.WriteLine("Escolha a turma:");
            for (int i = 0; i < turmas.Count; i++)
            {
                Console.WriteLine($"{i} - {turmas[i].Codigo}");
            }

            int t = int.Parse(Console.ReadLine());

            Console.WriteLine("Escolha o aluno:");
            for (int i = 0; i < alunos.Count; i++)
            {
                Console.WriteLine($"{i} - {alunos[i].GetNome()}");
            }

            int a = int.Parse(Console.ReadLine());

            turmas[t].AdicionarAluno(alunos[a]);

            Console.WriteLine("Aluno adicionado!");
        }

        static void LancarNota()
        {
            if (alunos.Count == 0)
            {
                Console.WriteLine("Sem alunos!");
                return;
            }

            Console.WriteLine("Escolha o aluno:");
            for (int i = 0; i < alunos.Count; i++)
            {
                Console.WriteLine($"{i} - {alunos[i].GetNome()}");
            }

            int a = int.Parse(Console.ReadLine());

            Console.Write("Nota: ");
            double nota = double.Parse(Console.ReadLine());

            alunos[a].AdicionarNota(nota);

            Console.WriteLine("Nota adicionada!");
        }

        
        static void ListarAlunos()
        {
            foreach (var aluno in alunos)
            {
                Console.WriteLine($"Nome: {aluno.GetNome()}");
                Console.WriteLine($"Média: {aluno.CalcularMedia()}");
                Console.WriteLine($"Situação: {aluno.ObterSituacao()}");
                Console.WriteLine("----------------------");
            }
        }
    }
}
