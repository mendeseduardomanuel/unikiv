using SistemaAcademico.Model;

namespace SistemaAcademico
{
    internal class Program
    {
        static List<Estudante> estudantes = new List<Estudante>();
        static List<Docente> docentes = new List<Docente>();
        static List<UnidadeCurricular> ucs = new List<UnidadeCurricular>();
        static void Main(string[] args)
        {
            int opcao;

            do
            {
                Console.WriteLine("\n===== SISTEMA UNIVERSITÁRIO =====");
                Console.WriteLine("1 - Cadastrar Estudante");
                Console.WriteLine("2 - Cadastrar Docente");
                Console.WriteLine("3 - Criar Unidade Curricular");
                Console.WriteLine("4 - Inscrever Estudante na UC");
                Console.WriteLine("5 - Adicionar Avaliações");
                Console.WriteLine("6 - Emitir Pauta");
                Console.WriteLine("0 - Sair");

                Console.Write("Opção: ");
                opcao = int.Parse(Console.ReadLine());

                switch (opcao)
                {
                    case 1: CadastrarEstudante(); break;
                    case 2: CadastrarDocente(); break;
                    case 3: CriarUC(); break;
                    case 4: InscreverEstudante(); break;
                    case 5: AdicionarAvaliacao(); break;
                    case 6: EmitirPauta(); break;
                }

            } while (opcao != 0);
        }

        static void CadastrarEstudante()
        {
            Console.Clear();

            Console.Write("Nome: ");
            string nome = Console.ReadLine();

            Console.Write("Idade: ");
            int idade = int.Parse(Console.ReadLine());

            Console.Write("Número: ");
            int numero = int.Parse(Console.ReadLine());

            estudantes.Add(new Estudante(nome, idade, numero));
            Console.WriteLine("Estudante cadastrado!");

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }

        static void CadastrarDocente()
        {
            Console.Clear();

            Console.Write("Nome: ");
            string nome = Console.ReadLine();

            Console.Write("Idade: ");
            int idade = int.Parse(Console.ReadLine());

            Console.WriteLine("1 - Titular | 2 - Assistente");
            int tipo = int.Parse(Console.ReadLine());

            if (tipo == 1)
                docentes.Add(new Titular(nome, idade));
            else
                docentes.Add(new Assistente(nome, idade));

            Console.WriteLine("Docente cadastrado!");

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }

        static void CriarUC()
        {
            Console.Clear();

            Console.Write("Nome da UC: ");
            string nome = Console.ReadLine();

            ucs.Add(new UnidadeCurricular(nome));
            Console.WriteLine("UC criada!");

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }

        static void InscreverEstudante()
        {
            Console.Clear();

            if (ucs.Count == 0 || estudantes.Count == 0)
            {
                Console.WriteLine("Cadastre UC e Estudantes primeiro.");
                return;
            }

            Console.WriteLine("\nEscolha UC:");
            for (int i = 0; i < ucs.Count; i++)
                Console.WriteLine($"{i} - {ucs[i].Nome}");

            int ucIndex = int.Parse(Console.ReadLine());

            Console.WriteLine("\nEscolha Estudante:");
            for (int i = 0; i < estudantes.Count; i++)
                Console.WriteLine($"{i} - {estudantes[i].Nome}");

            int estIndex = int.Parse(Console.ReadLine());

            ucs[ucIndex].Estudantes.Add(estudantes[estIndex]);

            Console.WriteLine("Estudante inscrito!");

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }

        static void AdicionarAvaliacao()
        {
            Console.Clear();

            if (ucs.Count == 0)
            {
                Console.WriteLine("Crie uma UC primeiro.");
                return;
            }

            Console.WriteLine("\nEscolha UC:");
            for (int i = 0; i < ucs.Count; i++)
                Console.WriteLine($"{i} - {ucs[i].Nome}");

            int ucIndex = int.Parse(Console.ReadLine());

            Console.WriteLine("1 - Teste | 2 - Projecto | 3 - Exame");
            int tipo = int.Parse(Console.ReadLine());

            Console.Write("Nota: ");
            double nota = double.Parse(Console.ReadLine());

            switch (tipo)
            {
                case 1:
                    ucs[ucIndex].Avaliacoes.Add(new Teste(nota));
                    break;
                case 2:
                    ucs[ucIndex].Avaliacoes.Add(new Projecto(nota));
                    break;
                case 3:
                    ucs[ucIndex].Avaliacoes.Add(new ExameFinal(nota));
                    break;
            }

            Console.WriteLine("Avaliação adicionada!");

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }

        static void EmitirPauta()
        {
            Console.Clear();

            if (ucs.Count == 0)
            {
                Console.WriteLine("Nenhuma UC disponível.");
                return;
            }

            Console.WriteLine("\nEscolha UC:");
            for (int i = 0; i < ucs.Count; i++)
                Console.WriteLine($"{i} - {ucs[i].Nome}");

            int ucIndex = int.Parse(Console.ReadLine());

            ucs[ucIndex].EmitirPauta();

            Console.WriteLine("\n Precione qualquer tecla para continuar...");
            Console.ReadKey();
            Console.Clear();
        }
    }
}
